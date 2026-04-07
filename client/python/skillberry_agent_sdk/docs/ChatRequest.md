# ChatRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**model** | **str** | Model to use, e.g., &#39;granite&#39; | 
**messages** | [**List[ChatMessage]**](ChatMessage.md) | List of messages for context | 
**temperature** | **float** | Sampling temperature | [optional] [default to 0.7]
**max_tokens** | **int** | Maximum number of tokens to generate | [optional] [default to 256]

## Example

```python
from skillberry_agent_sdk.models.chat_request import ChatRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ChatRequest from a JSON string
chat_request_instance = ChatRequest.from_json(json)
# print the JSON string representation of the object
print(ChatRequest.to_json())

# convert the object into a dict
chat_request_dict = chat_request_instance.to_dict()
# create an instance of ChatRequest from a dict
chat_request_from_dict = ChatRequest.from_dict(chat_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


