from query_gpt import Prompter
from prompts import prompt_with_history
import pandas as pd

def replace_observations(observation_prompts: pd.DataFrame, sequence: pd.DataFrame):
    observation_prompts = observation_prompts.copy()
    selected_columns = [column for column in sequence.columns if column.startswith("a")]
    sequence[selected_columns] = sequence[selected_columns].map(lambda x: observation_prompts.loc[x]["prompt"])

if __name__ == "__main__":
    observation_prompts = pd.read_csv("data/observation_prompts.csv", index_col=0)
    sequence = pd.read_csv("data/sequence.csv", index_col=0)
    replace_observations(observation_prompts, sequence)
    prompter = Prompter()

    actions = []
    for i, row in sequence.iterrows():
        action = prompter.test(list(row))
        prompter.reset()
        actions.append(pd.Series(action, name=f"a{i}"))
    actions = pd.DataFrame(actions)
    actions.to_csv("test.csv")
