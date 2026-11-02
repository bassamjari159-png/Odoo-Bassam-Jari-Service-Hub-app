import sys

import polib


if len(sys.argv) != 4:
    raise SystemExit("Usage: merge_i18n.py MANUAL_PO EXPORTED_PO OUTPUT_PO")

manual_path, exported_path, output_path = sys.argv[1:]
manual_po = polib.pofile(manual_path)
exported_po = polib.pofile(exported_path)

translations = {
    entry.msgid: entry.msgstr
    for entry in manual_po
    if entry.msgid and entry.msgstr
}

merged_count = 0
for entry in exported_po:
    translation = translations.get(entry.msgid)
    if translation:
        entry.msgstr = translation
        merged_count += 1

exported_po.metadata["Language"] = "ar_SY"
exported_po.metadata["Language-Team"] = "BASSAM JARI Service Hub"
exported_po.metadata["Last-Translator"] = "Engineer BASSAM JARI"
exported_po.save(output_path)

print(f"Merged {merged_count} Arabic translations into {output_path}")
