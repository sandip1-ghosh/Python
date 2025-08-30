#Write a Python program that manages a list of student scores. Perform the following operations step-by-step:

#Create an empty list to store scores.

#Append the scores: 85, 90, 78, 92, 88

#Insert the score 80 at index 

#Remove the score 92 from the list

#Sort the scores in ascending order

#Reverse the list

#Find and print the maximum and minimum score

#Check if 90 is in the list

#Print the total number of scores

#Slice and print the first three scores
 
#find the last element from the list

#replace the score with new score on the index 2

#create a new copied list also

 
Student_Score=[]
print("Empty List",Student_Score)

Student_Score.extend([85, 90, 78, 92, 88])
print("Extended list",Student_Score)

Student_Score.insert(5,80)
print("After inserting 80 at index 5",Student_Score)

Student_Score.remove(92)
print("After removing 92 from the list",Student_Score)

Student_Score.sort()
print("Sorted List",Student_Score)

Student_Score.reverse()
print("Reverse List",Student_Score)

print('Max score',max(Student_Score))

print('Min score',min(Student_Score))

print("Is 90 in the list?", 90 in Student_Score)

print("Length of list",len(Student_Score))

print("First three scores :", Student_Score[:3])

Lastelement=Student_Score[-1]
print("Last element of the list",Lastelement)

Student_Score[2]=95
print(Student_Score)

copyList=Student_Score.copy()
print("Copied List",copyList)
