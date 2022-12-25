import pandas as pd
import torch
from transformers import BertJapaneseTokenizer, BertModel

MODEL_NAME = 'cl-tohoku/bert-base-japanese-whole-word-masking'
tokenizer = BertJapaneseTokenizer.from_pretrained(MODEL_NAME)
model = BertModel.from_pretrained(MODEL_NAME)

path = "/Users/iomacbookair2/Documents/lab/DEIM2023/tweet_csv/221212_ann_mon.csv"
df = pd.read_csv((path))
df.sort_values(by='created_at', ascending=True, inplace=True)
df = df.reset_index(drop=True)
df['created_at'] = pd.to_datetime(df['created_at'])
df

groups = df.groupby(pd.Grouper(key='created_at', freq='min'))
df_texts_by_minute = pd.DataFrame({
    "texts_by_minute": groups.apply(lambda x: x["text"].tolist())
})
df_texts_by_minute = df_texts_by_minute.reset_index()
df_texts_by_minute

df_texts_by_minute.to_csv("texts_by_minute.csv", index=False)


def sentence_to_vector(model, tokenizer, sentence):
    tokens = tokenizer(sentence, add_special_tokens=True)["input_ids"]
    input = torch.tensor(tokens).unsqueeze(0)
    with torch.no_grad():
        outputs = model(input, output_hidden_states=True)
        last_hidden_state = outputs[0][:, 0, :]
        averaged_hidden_state = last_hidden_state.mean(dim=0).unsqueeze(0)
    return averaged_hidden_state


def calc_similarity(sentence1, sentence2):
    print("{}\n{}".format(sentence1, sentence2))

    sentence_vector1 = sentence_to_vector(model, tokenizer, sentence1)
    sentence_vector2 = sentence_to_vector(model, tokenizer, sentence2)

    # Reshape the tensors to 1D
    sentence_vector1 = sentence_vector1.reshape(-1)
    sentence_vector2 = sentence_vector2.reshape(-1)

    similarity = float(torch.nn.functional.cosine_similarity(
        sentence_vector1, sentence_vector2, dim=0).detach().numpy().copy())
    print("Similarity:", similarity)

    return similarity


def calc_average_similarity(sentences):
    similarities = []
    for i in range(1, len(sentences)):
        similarity = calc_similarity(sentences[0], sentences[i])
        similarities.append(similarity)
    average_similarity = sum(similarities) / len(similarities)
    print("Similarities:", similarities)
    print("Average similarity:", average_similarity)

    return average_similarity
