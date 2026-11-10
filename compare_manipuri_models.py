
import csv
import time
from pathlib import Path
from backend.translation.indictrans_service import indictrans_service
from backend.translation.manipuri_bengali_service import manipuri_bengali_service

TESTS=[
    {"text":"Hello, how are you?","source":"english"},
    {"text":"My name is Rahul.","source":"english"},
    {"text":"Thank you.","source":"english"},
    {"text":"What is your name?","source":"english"},
    {"text":"Where do you live?","source":"english"},
    {"text":"I need your help.","source":"english"},
    {"text":"नमस्ते, आप कैसे हैं?","source":"hindi"},
    {"text":"मेरा नाम राहुल है।","source":"hindi"},
    {"text":"धन्यवाद।","source":"hindi"},
    {"text":"आपका नाम क्या है?","source":"hindi"},
    {"text":"आप कहाँ रहते हैं?","source":"hindi"},
    {"text":"मुझे आपकी मदद चाहिए।","source":"hindi"}
]

def has_bengali(text,threshold=0.80):
    letters=[
        char for char in text
        if char.isalpha()
    ]
    if not letters:
        return False
    bengali=sum(
        0x0980<=ord(char)<=0x09FF
        for char in letters
    )
    return bengali/len(letters)>=threshold
def run_indictrans(text,source):
    start=time.perf_counter()
    output=indictrans_service.translate(
        text=text,
        source_language=source,
        target_language="manipuri"
    )
    return output,time.perf_counter()-start

def run_alternative(text,source):
    start=time.perf_counter()
    output=manipuri_bengali_service.translate(
        text=text,
        source_language=source
    )
    return output,time.perf_counter()-start

def safe_run(function,text,source):
    try:
        output,elapsed=function(text,source)
        return output,elapsed,"OK"
    except Exception as error:
        return "",0.0,str(error)

def main():
    results=[]
    print("\n"+"="*100)
    print("MANIPURI BENGALI MODEL COMPARISON")
    print("="*100)

    for index,test in enumerate(TESTS,1):
        text=test["text"]
        source=test["source"]

        print(f"\n[{index}/{len(TESTS)}] {source.upper()}: {text}")

        old_output,old_time,old_status=safe_run(
            run_indictrans,text,source
        )
        new_output,new_time,new_status=safe_run(
            run_alternative,text,source
        )

        old_script=has_bengali(old_output)
        new_script=has_bengali(new_output)

        print("\nIndicTrans2:")
        print("Output:",old_output or "ERROR")
        print("Bengali script:",old_script)
        print("Time:",round(old_time,2),"seconds")
        if old_status!="OK":
            print("Error:",old_status)

        print("\nAlternative model:")
        print("Output:",new_output or "ERROR")
        print("Bengali script:",new_script)
        print("Time:",round(new_time,2),"seconds")
        if new_status!="OK":
            print("Error:",new_status)

        results.append({
            "source":source,
            "input":text,
            "indictrans_output":old_output,
            "indictrans_bengali":old_script,
            "indictrans_seconds":round(old_time,3),
            "indictrans_status":old_status,
            "alternative_output":new_output,
            "alternative_bengali":new_script,
            "alternative_seconds":round(new_time,3),
            "alternative_status":new_status
        })

    output_file=Path("manipuri_model_comparison.csv")

    with output_file.open("w",newline="",encoding="utf-8-sig") as file:
        writer=csv.DictWriter(file,fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    old_pass=sum(row["indictrans_bengali"] for row in results)
    new_pass=sum(row["alternative_bengali"] for row in results)
    total=len(results)

    print("\n"+"="*100)
    print("FINAL SUMMARY")
    print("="*100)
    print(f"Total tests: {total}")
    print(f"IndicTrans2 Bengali-script outputs: {old_pass}/{total}")
    print(f"Alternative Bengali-script outputs: {new_pass}/{total}")
    print(f"IndicTrans2 script rate: {old_pass/total*100:.1f}%")
    print(f"Alternative script rate: {new_pass/total*100:.1f}%")
    print(f"\nResults saved to: {output_file.resolve()}")
    print("\nNote: Script detection does not measure translation accuracy.")

if __name__=="__main__":
    main()