"""
This script exists for the purpose of transforming the following features
(under "author", "professional"):

- professional_type
- category

These features go hand-in-hand, meaning that most of the time if 
"professional_type" is defined, so is "category". Although that 
might not be always the case. 

In our dataset these features have the following values:

professional_type -> {null, "Business", "Creator"}
category -> {null, "Media & News Company", "Media Personality" etc.}

More importantly "category" has about 40 different values in our dataset. 
"professional_type" is not very important on its own, but can be 
important together with "category". The point of this script is to 
organize these categories into 4 broad categories, with accordance 
to "professional_type".

"""