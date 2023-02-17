# -*- coding: utf-8 -*

# =============================================================================
# Caricamento modelli e dataframe
# =============================================================================
import os
import pandas as pd 
import pyreadstat
import openai

os.chdir('C:\\Users\\Vahin\\Desktop')

# campioni
A = pd.read_spss("Letta_primaweek_campione.sav")
B = pd.read_spss("Letta_secondaweek_campione.sav")
C = pd.read_spss("Letta_terzaweek_campione.sav")
D = pd.read_spss("Letta_quartaweek_campione.sav")
E = pd.read_spss("Letta_electionday_campione.sav")

# =============================================================================
# Pulizia dei dati preliminare
# =============================================================================

# sistemazione della variabile Incivility e unificazione dei campioni
B = B.rename(columns={'iNCIVILITY': 'Incivility'})
B['Incivility']= B['Incivility'].apply(str)
B['Incivility'] = B['Incivility'].apply(str.lower)
D['Incivility']= D['Incivility'].apply(str)
D['Incivility'] = D['Incivility'].apply(str.lower)

df1 = pd.concat([A, B, C, D, E], ignore_index=True)

df2 = df1[['text', 'Incivility']]
df2 = df2[df2.text != ""]
df2['Incivility'] = df2['Incivility'].str.replace('non incivile','civile')

# determinazione del numero di righe con frasi civili e incivili
df2[df2.Incivility == 'incivile'].shape[0]

# divisione del dataset in base al contenuto della variabile Incivility
df3 = df2.groupby(['Incivility'])
df3 = df3.get_group("civile")

df4 = df2.groupby(['Incivility'])
df4 = df4.get_group("incivile")

# eliminazione dei duplicati, per purificare il campione
df3 = df3.drop_duplicates(subset=["text"], keep=False)
df4 = df4.drop_duplicates(subset=["text"], keep=False)  

# eliminazione di righe casuali di testi civili, in base da tenere il rapporto tra tweet incivili e civili al 50%
df3 = df3.iloc[:205]

# sovrascrittura del dataset precedente
df2 = pd.concat([df3, df4], ignore_index=True)

# =============================================================================
# Conversione in jsonlines e routine per la creazione del modello fine-tuned
# =============================================================================

# preparazione per la conversione del campione in jsonlines (la conversione avverrà su Anaconda Powershell)
df2 = df2.rename(columns={'text': 'prompt', 'Incivility': 'completion'})
df2.to_csv("training.csv")

'''
PROCEDURA PER LA CONVERSIONE:
        - settare la working directory
        - copincollare la seguente riga di comando: openai tools fine_tunes.prepare_data -f training.csv
        - seguire le procedure illustrare nella powershell, includendo anche le feature raccomandate da OpenAI
'''

# validazione della key di OpenAI e caricamento dei file nel server
openai.api_key = "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"

# caricamento dei dataset di training e validazione
openai.File.create(
  file=open("training_prepared_train (1).jsonl", "rb"),
  purpose='fine-tune'
)

openai.File.create(
  file=open("training_prepared_valid (1).jsonl", "rb"),
  purpose='fine-tune'
)

# creazione del modello di fine-tuning
openai.FineTune.create(training_file="file-GjiBh7Yj1Rh5T933h8tDjWmi", validation_file="file-uZkmdCtJeM1ndoRTYbtdLLH1", model="ada")

# comandi per seguire in tempo reale lo stato di lavorazione del modello
openai.FineTune.list()
openai.FineTune.retrieve(id="ft-8QHempTcmtWUcQODWLvtRV9B")
openai.FineTune.list_events(id="ft-8QHempTcmtWUcQODWLvtRV9B")

# =============================================================================
# Creazione delle completion e iterazione del modello su più dati = passare al file R scritto da Giglietto
# =============================================================================


