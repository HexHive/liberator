# Manual Initialized Variables

Vars need to be initialized:

```C
UriUriA baseUri;
stateA.uri = &baseUri;
```

```C
UriQueryListA * queryList = NULL; // this one
int itemCount = 0;
const int res = uriDissectQueryMallocA(&queryList, &itemCount,
    queryString, queryString + strlen(queryString));
```