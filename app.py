import streamlit as st
import pandas as pd
import subprocess
from PIL import Image
import base64
import pickle

# Molecular descriptor calculator
def desc_calc():
    # Performs the descriptor calculation
    bashCommand = "java -Xms2G -Xmx2G -Djava -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


# File download
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

# Model building
def build_model(input_data):
    # Reads in saved regression model
    load_model = pickle.load(open('cd73_model.pkl', 'rb'))
    # Apply model to make predictions
    prediction = load_model.predict(input_data)
    st.header('**Prediction output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)

# Page title bigger
st.title('CD73 Inhibitor Bioactivity Prediction App')

st.write("""My analysis is essentially grounded in the concept of a YouTube channel,
          as exemplified by the work showcased on the platform of DataProfessor,
          accessible through the following link: https://www.youtube.com/@DataProfessor.""")

# Logo image
image = Image.open('logo.png')

st.image(image, use_column_width=True)


#


st.write("""
Tumors, a disease with a high mortality rate worldwide, have become a serious threat to human health.
             Exonucleotide-5'-nucleotidase (CD73) is an emerging target for tumor therapy.
             Its inhibition can significantly reduce adenosine levels in the tumor microenvironment.
             In the immune response, extracellular ATP exerts immune efficacy by activating T cells.
             However, dead tumor cells release excess ATP, overexpress CD39 and CD73 on the cell membrane and catabolize this ATP to adenosine.
             This leads to further immunosuppression. There are a number of inhibitors of CD73 currently under investigation.(Zhang et al., 2023). 
""")



#add image
image = Image.open('cd73.png')

st.image(image, use_column_width=True)
st.write("Image from www.bellbrooklabs.com")

st.write("In this web application, we will be using a machine learning model to predict the bioactivity of CD73 inhibitors.")

uploaded_file = st.file_uploader("Upload your input file", type=['txt'])
st.write("""Your file text need to have the following format:
    - Column 1: SMILES
    - Column 2: Molecule name (ID, name or others)
            """)
st.markdown("""
[Example input file](https://github.com/FrancescoRec/CD73_analyzer/blob/main/example_for_app.txt)
""")

if st.button('Predict'):
    load_data = pd.read_table(uploaded_file, sep=' ', header=None)
    load_data.to_csv('molecule.smi', sep='\t', header=False, index=False)

    st.header('**Original input data**')
    st.write(load_data)

    with st.spinner("Calculating descriptors..."):
        desc_calc()

    # Read in calculated descriptors and display the dataframe
    desc = pd.read_csv('descriptors_output.csv')


    # Read descriptor list used in previously built model
    Xlist = list(pd.read_csv('descriptor_list.csv').columns)
    desc_subset = desc[Xlist]


    # Apply trained model to make prediction on query compounds
    build_model(desc_subset)
else:
    st.info('Upload input data to start!')
