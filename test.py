with open("seq.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

print("Total lines in file:", len(lines))

# Print first and last 5 lines for verification
print("\nFirst 5 lines:")
i=0
for line in lines[:385]:
    i=i+1
    print(line.strip(),i)