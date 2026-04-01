# skillberry_agent_sdk.ChatApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_chat_completion_chat_completions_post**](ChatApi.md#api_chat_completion_chat_completions_post) | **POST** /chat/completions | Api Chat Completion
[**api_chat_completion_v1_chat_completions_post**](ChatApi.md#api_chat_completion_v1_chat_completions_post) | **POST** /v1/chat/completions | Api Chat Completion
[**api_prompt_prompt_post**](ChatApi.md#api_prompt_prompt_post) | **POST** /prompt | Api Prompt


# **api_chat_completion_chat_completions_post**
> object api_chat_completion_chat_completions_post(chat_request)

Api Chat Completion

### Example


```python
import skillberry_agent_sdk
from skillberry_agent_sdk.models.chat_request import ChatRequest
from skillberry_agent_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = skillberry_agent_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with skillberry_agent_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = skillberry_agent_sdk.ChatApi(api_client)
    chat_request = skillberry_agent_sdk.ChatRequest() # ChatRequest | 

    try:
        # Api Chat Completion
        api_response = api_instance.api_chat_completion_chat_completions_post(chat_request)
        print("The response of ChatApi->api_chat_completion_chat_completions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->api_chat_completion_chat_completions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chat_request** | [**ChatRequest**](ChatRequest.md)|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_chat_completion_v1_chat_completions_post**
> object api_chat_completion_v1_chat_completions_post(chat_request)

Api Chat Completion

### Example


```python
import skillberry_agent_sdk
from skillberry_agent_sdk.models.chat_request import ChatRequest
from skillberry_agent_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = skillberry_agent_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with skillberry_agent_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = skillberry_agent_sdk.ChatApi(api_client)
    chat_request = skillberry_agent_sdk.ChatRequest() # ChatRequest | 

    try:
        # Api Chat Completion
        api_response = api_instance.api_chat_completion_v1_chat_completions_post(chat_request)
        print("The response of ChatApi->api_chat_completion_v1_chat_completions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->api_chat_completion_v1_chat_completions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chat_request** | [**ChatRequest**](ChatRequest.md)|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_prompt_prompt_post**
> object api_prompt_prompt_post(user_prompt)

Api Prompt

### Example


```python
import skillberry_agent_sdk
from skillberry_agent_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = skillberry_agent_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with skillberry_agent_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = skillberry_agent_sdk.ChatApi(api_client)
    user_prompt = 'user_prompt_example' # str | 

    try:
        # Api Prompt
        api_response = api_instance.api_prompt_prompt_post(user_prompt)
        print("The response of ChatApi->api_prompt_prompt_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->api_prompt_prompt_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_prompt** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

