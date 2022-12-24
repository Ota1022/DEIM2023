import torch
from transformers import BertJapaneseTokenizer, BertModel


def sentence_to_vector(model, tokenizer, sentence):
    tokens = tokenizer(sentence, add_special_tokens=True)["input_ids"]
    input = torch.tensor(tokens).unsqueeze(0)
    with torch.no_grad():
        outputs = model(input)
        last_hidden_state = outputs[0]
        averaged_hidden_state = last_hidden_state.mean(dim=0).unsqueeze(0)
    return averaged_hidden_state


def calc_similarity(sentence1, sentence2):
    print("{}\n{}".format(sentence1, sentence2))

    sentence_vector1 = sentence_to_vector(model, tokenizer, sentence1)
    sentence_vector2 = sentence_to_vector(model, tokenizer, sentence2)

    # Calculate the cosine similarity
    score = torch.nn.functional.cosine_similarity(
        sentence_vector1, sentence_vector2, dim=0).detach().numpy().copy()
    print("Similarity:", score)


MODEL_NAME = 'cl-tohoku/bert-base-japanese-whole-word-masking'
tokenizer = BertJapaneseTokenizer.from_pretrained(MODEL_NAME)
model = BertModel.from_pretrained(MODEL_NAME)
sentence = "我輩は猫である。"
sentence_vector = sentence_to_vector(model, tokenizer, sentence)
sentence1 = "吾輩は猫である"
sentence2 = "私は猫です"

calc_similarity(sentence1, sentence2)
