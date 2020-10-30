
# stringToEdit = ""
stringToEdit = input()
editedString = "("

listToEdit = stringToEdit.split(" ")
print(stringToEdit)
print(listToEdit)

for word in listToEdit:
    if word.isdigit():
        editedString = editedString[: len(editedString)-1] + ") " + ", \n("
        word = word + ","
        editedString = editedString + word
    else:
        editedString = editedString + word + ","

print(editedString)
