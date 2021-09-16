import copy


class DFA:

    def __init__(self, keyword_list: list):
        self.state_event_dict = self._generate_state_event_dict(keyword_list)

    def match(self, content: str):
        match_list = []
        state_list = []
        temp_match_list = []

        for char_pos, char in enumerate(content):
            if char in self.state_event_dict:
                state_list.append(self.state_event_dict)
                temp_match_list.append({
                    "keyword":"",
                    "match": ""
                })

            for index, state in enumerate(state_list):
                if char in state:
                    state_list[index] = state[char]
                    temp_match_list[index]["match"] += char
                    temp_match_list[index]["keyword"] += char

                    if state[char]["is_end"]:
                        match_list.append(copy.deepcopy(temp_match_list[index]))

                else:
                    state_list.pop(index)
                    temp_match_list.pop(index)

        return match_list

    @staticmethod
    def _generate_state_event_dict(keyword_list: list) -> dict:
        state_event_dict = {}

        for keyword in keyword_list:
            current_dict = state_event_dict
            length = len(keyword)

            for index, char in enumerate(keyword):
                if char not in current_dict:
                    next_dict = {"is_end": False}
                    current_dict[char] = next_dict
                    current_dict = next_dict
                else:
                    next_dict = current_dict[char]
                    current_dict = next_dict

                if index == length - 1:
                    current_dict["is_end"] = True

        return state_event_dict


if __name__ == "__main__":
    dfa = DFA(["fqwe","fuck"])
    print(dfa.match("afuck"))
