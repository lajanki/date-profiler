# date-profiler
A Flask webapp for generating dating profiles based on Google Search autocomplete suggestions. 

https://date-profiler-dot-webhost-common.appspot.com/


## About
A set of profile templates from `data/date_profiles` directory with marked phrases to be used as search terms is randomly filled using Google Search autocomplete API http://suggestqueries.google.com/complete/search:

![Google search](/static/img/google_search_friends_tell_me.png)

This results in something like:
> I graduated from a five-year masters program in architecture three years ago. I'm career-driven and **is success worth it**. I'm very adventurous and like to live life on the edge. The words **random and systematic errors** describe me well. I'm pretty much game for anything. 
> 
> For example, I decided to dye my hair red... at 2AM with my best friend a couple days ago. Another example is **when i decided to wage holy war**, find a new job and an apartment all within a week. Or lastly, when I moved to Switzerland - I decided a month before I ended up leaving. I just love doing things without notice. 
>
> I have a **passion for food** and would love to experience more diverse cultures. I've traveled a lot in Europe, all over the United States, Puerto Rico, and Canada. I **plan to go or plan on going** next January and I'm eager to see the rest of the world. 

Rather than dynamically querying the API, a local cache of all possible search terms is maintained in a Cloud Storage bucket. This cache is refreshed periodically.


> [!IMPORTANT]  
> The API is undocumented and is not guarenteed to be stable!


Hosted on Google App Engine.

---


## Running locally
This project is managed through `uv`
 * https://docs.astral.sh/uv/


Install Python packages with  
```shell
uv sync
```  
Then, run in localhost with
```shell
uv run flask --app main:app run
```

## Unit tests
Unit tests can be run from the root folder with
```shell
uv run pytest
```

## Deploy to Google App Engine
Production deployment is done via GitHub Actions.
