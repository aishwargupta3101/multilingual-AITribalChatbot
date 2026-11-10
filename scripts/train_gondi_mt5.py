"""Fine-tune google/mt5-small for Hindi <-> Gondi using a local AdiBhasha CSV.

By default this trains on the full CSV for one epoch. For a wiring smoke test,
pass --max-samples 200. Do not treat a smoke-test checkpoint as production-ready.
"""
from __future__ import annotations

import argparse
import csv
import os
import random
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "gondi" / "gondi-train.csv"
DEFAULT_OUTPUT = ROOT / "models" / "gondi_mt5"
BASE_MODEL = "google/mt5-small"


def _norm_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def read_parallel_csv(path: Path) -> list[tuple[str, str]]:
    """Read an AdiBhasha-like CSV and robustly find Hindi and Gondi columns."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Training CSV not found: {path}. Run `python scripts/download_gondi_adibhasha.py` first."
        )
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(8192)
        handle.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(handle, dialect=dialect)
        headers = reader.fieldnames or []
        if len(headers) < 2:
            raise ValueError(f"Expected at least two CSV columns; found headers: {headers!r}")
        normalized = {_norm_header(header): header for header in headers}
        hindi_col = next((original for norm, original in normalized.items() if norm in {"hindi", "hi", "hinditext", "hindi sentence", "sourcehindi".replace(" ", "")} or "hindi" in norm), None)
        gondi_col = next((original for norm, original in normalized.items() if norm in {"gondi", "gon", "gonditext", "gondisentence", "targetgondi"} or "gondi" in norm), None)
        if hindi_col is None or gondi_col is None:
            source_col = next((original for norm, original in normalized.items() if norm in {"source", "sourcetext", "sourceText".lower()}), None)
            target_col = next((original for norm, original in normalized.items() if norm in {"target", "targettext"}), None)
            if source_col and target_col:
                hindi_col, gondi_col = source_col, target_col
            elif len(headers) == 2:
                # AdiBhasha file is documented as Hindi-Gondi; assume source then target.
                hindi_col, gondi_col = headers[0], headers[1]
            else:
                raise ValueError(
                    f"Could not identify Hindi/Gondi columns in {headers!r}. "
                    "Check the downloaded AdiBhasha CSV headers before training."
                )
        pairs: list[tuple[str, str]] = []
        for row in reader:
            hindi = str(row.get(hindi_col, "") or "").strip()
            gondi = str(row.get(gondi_col, "") or "").strip()
            if hindi and gondi:
                pairs.append((hindi, gondi))
    if not pairs:
        raise ValueError(f"No usable Hindi-Gondi pairs found in {path}.")
    return pairs


def make_examples(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    examples: list[tuple[str, str]] = []
    for hindi, gondi in pairs:
        examples.append((f"translate Hindi to Gondi: {hindi}", gondi))
        examples.append((f"translate Gondi to Hindi: {gondi}", hindi))
    return examples


class TokenizedPairs:
    def __init__(self, examples: list[tuple[str, str]], tokenizer: Any, max_length: int):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        source, target = self.examples[index]
        source_tokens = self.tokenizer(source, truncation=True, max_length=self.max_length)
        target_tokens = self.tokenizer(text_target=target, truncation=True, max_length=self.max_length)
        return {
            "input_ids": source_tokens["input_ids"],
            "attention_mask": source_tokens["attention_mask"],
            "labels": target_tokens["input_ids"],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--base-model", default=BASE_MODEL)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--max-samples", type=int, default=0, help="0 uses the full CSV; use 200 for a wiring smoke test")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=160)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    args = parser.parse_args()

    try:
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, DataCollatorForSeq2Seq
        from torch.utils.data import DataLoader
    except ImportError as exc:
        print(f"Missing training dependency: {exc}. Install the specific missing package into this .venv, not a new environment.")
        return 2

    try:
        pairs = read_parallel_csv(args.data_csv)
    except (OSError, ValueError) as exc:
        print(f"DATA ERROR: {exc}")
        return 2
    random.Random(42).shuffle(pairs)
    if args.max_samples > 0:
        pairs = pairs[:args.max_samples]
    if len(pairs) < 20:
        print(f"Only {len(pairs)} pairs were found. Provide a valid dataset before fine-tuning.")
        return 2

    split = max(1, int(len(pairs) * 0.9))
    train_pairs, valid_pairs = pairs[:split], pairs[split:]
    train_examples, valid_examples = make_examples(train_pairs), make_examples(valid_pairs or train_pairs[: min(10, len(train_pairs))])
    print(f"Pairs: {len(pairs)} | bidirectional train examples: {len(train_examples)} | validation examples: {len(valid_examples)}")
    print(f"Base model: {args.base_model}")
    print("Note: training time depends on CPU/GPU and data size. This does not run a model benchmark.")

    try:
        tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=False)
        model = AutoModelForSeq2SeqLM.from_pretrained(args.base_model)
    except Exception as exc:
        print(f"Could not load base model {args.base_model}: {type(exc).__name__}: {exc}")
        return 2

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model, padding=True)
    train_data = TokenizedPairs(train_examples, tokenizer, args.max_length)
    valid_data = TokenizedPairs(valid_examples, tokenizer, args.max_length)
    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True, collate_fn=collator, num_workers=0)
    valid_loader = DataLoader(valid_data, batch_size=args.batch_size, shuffle=False, collate_fn=collator, num_workers=0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    grad_accum = max(1, args.gradient_accumulation_steps)
    try:
        from tqdm.auto import tqdm
    except ImportError:
        tqdm = lambda values, **kwargs: values  # simple fallback

    for epoch in range(args.epochs):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        running_loss = 0.0
        for step, batch in enumerate(tqdm(train_loader, desc=f"Epoch {epoch + 1}/{args.epochs}"), start=1):
            batch = {key: value.to(device) for key, value in batch.items()}
            loss = model(**batch).loss
            (loss / grad_accum).backward()
            running_loss += float(loss.detach().cpu())
            if step % grad_accum == 0 or step == len(train_loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
            if step % 100 == 0:
                print(f"epoch={epoch + 1} step={step}/{len(train_loader)} mean_loss={running_loss / step:.4f}")
        model.eval()
        val_losses = []
        with torch.inference_mode():
            for batch in tqdm(valid_loader, desc="Validation"):
                batch = {key: value.to(device) for key, value in batch.items()}
                val_losses.append(float(model(**batch).loss.detach().cpu()))
        print(f"Epoch {epoch + 1}: train_loss={running_loss / max(1, len(train_loader)):.4f}; validation_loss={sum(val_losses) / max(1, len(val_losses)):.4f}")
        model.save_pretrained(args.output_dir)
        tokenizer.save_pretrained(args.output_dir)
        print(f"Saved checkpoint after epoch {epoch + 1}: {args.output_dir}")

    print("Training finished. Validate generated Hindi-Gondi examples with Gondi speakers before relying on the model.")
    print("AdiBhasha is CC BY-NC-SA 4.0; this checkpoint/data are not for commercial use without separate permission.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
