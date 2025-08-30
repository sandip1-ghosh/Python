score= int(input("Enter a score:"))
print("Score entered by the user ",score)

if score > 90:
    grade='A'
else:
    if score > 80:
        grade='B'
    else:
        if score > 70:
            grade='C'
        else:
            if score > 60:
                grade='D'
            else:
                grade='F'
print("Final grade for score",score,"is",grade)

