import pandas as pd

file = open('files/sample_input.html', 'r', encoding='utf-8')

tables = pd.read_html(file, na_values=None, keep_default_na=False)
table = tables[0]
content: pd.Series = table.get(table.columns[2])
dict_repr = content.to_dict()
otp = pd.DataFrame()
index = 0
for i, value in dict_repr.items():
    day = table.get(table.columns[0])[i]
    pair_no = table.get(table.columns[1])[i]
    if not day and not pair_no:
        continue
    index += 1
    df = pd.DataFrame(
                {
                    'Day': day,
                    'Pair No': pair_no,
                    'Value': value
                },
                index=[index]
            )
    otp = pd.concat(
        [
            otp,
            df
        ]
    )

with open('files/sample_out.html', 'w', encoding='utf-8') as f:
    otp.to_html(f, index=None)