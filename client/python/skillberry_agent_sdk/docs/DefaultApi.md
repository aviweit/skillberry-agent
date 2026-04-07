# skillberry_agent_sdk.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_disconnect_disconnect_post**](DefaultApi.md#api_disconnect_disconnect_post) | **POST** /disconnect | Api Disconnect
[**get_trajectory_trajectory_get**](DefaultApi.md#get_trajectory_trajectory_get) | **GET** /trajectory | Get Trajectory
[**health_check_health_get**](DefaultApi.md#health_check_health_get) | **GET** /health | Health Check
[**health_check_version_get**](DefaultApi.md#health_check_version_get) | **GET** /version | Health Check


# **api_disconnect_disconnect_post**
> object api_disconnect_disconnect_post()

Api Disconnect

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
    api_instance = skillberry_agent_sdk.DefaultApi(api_client)

    try:
        # Api Disconnect
        api_response = api_instance.api_disconnect_disconnect_post()
        print("The response of DefaultApi->api_disconnect_disconnect_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->api_disconnect_disconnect_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_trajectory_trajectory_get**
> object get_trajectory_trajectory_get()

Get Trajectory

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
    api_instance = skillberry_agent_sdk.DefaultApi(api_client)

    try:
        # Get Trajectory
        api_response = api_instance.get_trajectory_trajectory_get()
        print("The response of DefaultApi->get_trajectory_trajectory_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_trajectory_trajectory_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **health_check_health_get**
> object health_check_health_get()

Health Check

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
    api_instance = skillberry_agent_sdk.DefaultApi(api_client)

    try:
        # Health Check
        api_response = api_instance.health_check_health_get()
        print("The response of DefaultApi->health_check_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->health_check_health_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **health_check_version_get**
> object health_check_version_get()

Health Check

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
    api_instance = skillberry_agent_sdk.DefaultApi(api_client)

    try:
        # Health Check
        api_response = api_instance.health_check_version_get()
        print("The response of DefaultApi->health_check_version_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->health_check_version_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

