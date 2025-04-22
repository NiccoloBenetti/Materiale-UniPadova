# Getting Started with the Foundry SDK on Azure Machine Learning

This guide provides a structured walkthrough to help you set up and explore the Foundry SDK within Azure Machine Learning Studio.  

<br>

## Project Structure

The project is organized into a series of folders that group notebooks by topic:

- `01-SDK_Basic_Operations`: Notebooks covering the fundamental operations of the SDK.
- `02-Agent_Service`: Scripts and examples related to the Agent Service.
- `03-Document_Intelligence`: Notebooks focused on the document intelligence service (formerly Form Recognizer).
- `04-Content_Understanding`: Notebooks that cover the Content Understanding service.
- `05-SDK_Evaluation`: Tools and tests for evaluating SDK performance, accuracy and more.
- `06-SDK_RAG`: This folder is **not** meant to be executed within a notebook environment. Instead, it contains a complete end-to-end demo that should be downloaded and run locally on your IDE.

---

- `data/`: Contains supporting assets used across notebooks.
- `infra/`: Infrastructure files necessary to set up the environment.

<br>

## Setting up the Machine Learning Studio environment

This guide walks you through setting up an environment on Azure to run notebooks to explore the Foundry SDK.

---

### 1. Creating the Azure Machine Learning Workspace

Create an **Azure Machine Learning** resource within an existing or new **Resource Group** using the Azure portal.  
Once the deployment is complete, access the workspace and click the **"Launch studio"** button to enter the development environment.

---

### 2. Uploading the Working Folder

Inside the **Azure Machine Learning studio**, go to the **"Notebooks"** section and upload the entire **working folder** containing the necessary files to use the Foundry SDK.

---

### 3. Creating the Compute Instance

Create a new **compute instance** within the studio, selecting the **smallest available size** for the virtual machine — it will be sufficient to run the Foundry SDK notebook.

---

### 4. Configuring the Python Environment in the Terminal

Open the **terminal** inside Azure Machine Learning studio and follow these steps to create and configure a custom Python environment:

Replace **your_env** with your preferred environment name.

- Deactivate the default Conda environment
```bash
conda deactivate
```

- Create a new Python 3.10 environment
```bash
conda create -n your_env python=3.10
```

- Activate the new environment
```bash
conda activate your_env
```

- Install the required libraries
```bash
pip install -r infra/requirements.txt
```

- Register the environment kernel in the workspace
```bash
python -m ipykernel install --name your_env --user
```

---

### 5. Opening JupyterLab

- Go to the **Compute** section inside the studio and click **"Jupyter"** next to your compute instance to open the development environment.  
- Navigate into the **01-SDK_Basic_Operations** folder and open the notebook inside.  
- When prompted to select a kernel, choose the one you created in the previous step (`your_env` or the name you used).
- You can now start exploring the Foundry SDK!
