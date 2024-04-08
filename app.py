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
    try:
        load_model = pickle.load(open('cd73_model.pkl', 'rb'))
    except FileNotFoundError:
        st.error("Model file 'cd73_model.pkl' not found. Please make sure the file exists.")
    # Apply model to make predictions
    try:
        prediction = load_model.predict(input_data)
    except Exception as e:
        st.error(f"Error occurred during prediction: {e}")

    st.header('**Prediction output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)

# Function to reset the page
def reset_page():
    st.experimental_rerun()

# Page title
st.title('CD73 Inhibitor Bioactivity Prediction App')
st.write("""By Francesco D'Aleo""")

# Introduction
st.write("""This app is inspired from the content featured on the YouTube channel located at https://www.youtube.com/@DataProfessor.""")
st.write("""The purpose of this app is to predict the bioactivity of CD73 inhibitors using molecular descriptors from the PaDEL-Descriptor software.
         These features are then used to train a machine learning model on the CD73 dataset. The user can input a molecule in the form of a SMILES string or upload a file containing multiple molecules.""")
# Logo image
image = Image.open('logo.png')
st.image(image, use_column_width=True)

# Information about CD73
st.write("""
Tumors, a disease with a high mortality rate worldwide, have become a serious threat to human health.
             Exonucleotide-5'-nucleotidase (CD73) is an emerging target for tumor therapy.
             Its inhibition can significantly reduce adenosine levels in the tumor microenvironment.
             In the immune response, extracellular ATP exerts immune efficacy by activating T cells.
             However, dead tumor cells release excess ATP, overexpress CD39 and CD73 on the cell membrane and catabolize this ATP to adenosine.
             This leads to further immunosuppression. There are a number of inhibitors of CD73 currently under investigation.(Zhang et al., 2023). 
""")

# CD73 image
cd73_image = Image.open('CD73.png')
st.image(cd73_image, use_column_width=True)
st.write("Image from www.bellbrooklabs.com")

st.write("You can test one molecule or multiple molecules by uploading a text file.")


# Main functionality
option = st.selectbox("Select an option", ["Predict molecule", "Predict file"])
if option == "Predict molecule":
    smiles_input = st.text_input("Enter SMILES string:")
    molecule_id = st.text_input("Enter molecule ID:", "test_molecule")
    if st.button('Predict molecule'):
        smiles_list = [smiles_input]
        names_list = [molecule_id]
        load_data = pd.DataFrame(list(zip(smiles_list, names_list)))
        load_data.to_csv('molecule.smi', sep='\t', header=False, index=False)

        st.header('**Input molecule**')
        st.write(load_data)

        with st.spinner("Calculating descriptors..."):
            desc_calc()

        desc = pd.read_csv('descriptors_output.csv')
        Xlist = list(pd.read_csv('descriptor_list.csv').columns)
        desc_subset = desc[Xlist]

        build_model(desc_subset)
elif option == "Predict file":
    uploaded_file = st.file_uploader("Upload your input file", type=['txt'])
    st.write("""Your file text need to have the following format:
        - Column 1: SMILES
        - Column 2: Molecule name (ID, name or others)""")
    st.markdown("""
    [Example input file](https://github.com/FrancescoRec/CD73_analyzer/blob/main/example_for_app.txt)
    """)

    if st.button('Predict file'):
        load_data = pd.read_table(uploaded_file, sep=' ', header=None)
        load_data.to_csv('molecule.smi', sep='\t', header=False, index=False)

        st.header('**Original input data**')
        st.write(load_data)

        with st.spinner("Calculating descriptors..."):
            desc_calc()

        desc = pd.read_csv('descriptors_output.csv')
        Xlist = list(pd.read_csv('descriptor_list.csv').columns)
        desc_subset = desc[Xlist]

        build_model(desc_subset)

# Reset button
if st.button('Reset'):
    reset_page()
