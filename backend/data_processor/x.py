from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size = 25,
    chunk_overlap  = 0,
    length_function = len,
    separators=["\n\n", "\n", "   ", " ", ""]
)

#texts = text_splitter.split_text(source)

text = """


Home


> Benefits




Use Light to Clean Air and Buildings






Transform Almost Any Surface into a Self-Cleaning Air Purifier to Save More and Clean Less
 
PURETi treated surfaces prevent grime growth and reverse pollution outdoors. Indoors, PURETi eliminates odors and improves air quality. Buildings and windows stay cleaner. White roofs stay cooler. Inside air is healthier and odor free. One long lasting application saves time, money, water, chemicals and energy.










Benefits
 




 Pollution Control


PURETi treated roads and buildings eat smog and reverse pollution by reducing criteria pollutants like NOx and PM 2.5. As powerful as planting trees.






 Self-Cleaning


Windows, roofs and facades stay twice as clean for twice as long with grime preventing PURETi. Building appearance is preserved and maintenance reduced.






 




 Odor Elimination


Scrubs air free of smoke, pet, food or human odors. PURETi doesnt mask odors. It breaks them down. Works great inside hotels, cars, homes or schools.






 IAQ Improvement


PURETi treated windows, window coverings and light fixtures act as air scrubbers to reduce VOCs in interior spaces by 50% or more.








 




 Sustainability


Saves energy with cooler roofs and cleaner PV panels. Saves water and chemicals with reduced washing. Enhances brand and building value. Helps earn LEED points.






 Cost Savings


PURETi pays for itself by reducing maintenance costs.  Hard ROI savings in labor, energy, water and chemical use


"""

text = """

 


Home

 > 
Industries


> Auto




Protect Your Family with a Cleaner, Healthier Car
 
The PURETi Healthy Car Care Program combines the power of hospital-grade surface disinfection and continuous, light-activated air purification to create healthier vehicle interiors.




The PURETi Healthy Car Care Program, available only through authorized dealers, is apreventative maintenaceservice that enhancesthe health and well being of you and your family. 
Contact us
 to find an authorizeddealer near you.


Click 
here
 to review the 2006 Ecology Center study

"""

chunks = []
fragments = []

# clean input
text.strip()
while text.find("\n\n\n") > -1:
    text = text.replace("\n\n\n", "\n\n")

# built array of fragments by nn
fragments = text.split('\n\n')

# add array elements until reaching an element with at least 20 words
cur_chunk = ""
for i, fragment in enumerate(fragments):
    if len(fragment) > 1:
        if i > 0:
            cur_chunk = cur_chunk  + "\n"
        cur_chunk = cur_chunk + fragment
    if len(cur_chunk) > 1 and (len(fragment.split()) >= 20 or i + 1 == len(fragments)):
        chunks.append(cur_chunk.strip())
        cur_chunk = ""


print("*************** FRAGMENTS ***************")
for fragment in fragments:
    print(fragment)
    print("-------------------------")
print("*************** CHUNKS ***************")
for chunk in chunks:
    print(chunk)
    print("-------------------------")




