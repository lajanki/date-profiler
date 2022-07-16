# date-profiler
https://date-profiler-dot-webhost-common.appspot.com/

A Flask based webapp for generating dating profiles based on Google Search autocomplete suggestions. 

## About
A set of fixed profile templates from `data/date_profiles/templates` directory with marked phrases to be used as search terms is randomly filled using Google Search autocomplete API http://suggestqueries.google.com/complete/search:

![Google search](/static/img/google_search_friends_tell_me.png)

This results in something like:
> I graduated from a five-year masters program in architecture three years ago. I'm career-driven and **is success worth it**. I'm very adventurous and like to live life on the edge. The words **random and systematic errors** describe me well. I'm pretty much game for anything. 
> 
> For example, I decided to dye my hair red... at 2AM with my best friend a couple days ago. Another example is **when i decided to wage holy war**, find a new job and an apartment all within a week. Or lastly, when I moved to Switzerland - I decided a month before I ended up leaving. I just love doing things without notice. 
>
> I have a **passion for food** and would love to experience more diverse cultures. I've traveled a lot in Europe, all over the United States, Puerto Rico, and Canada. I **plan to go or plan on going** next January and I'm eager to see the rest of the world. 

Rather than dynamically querying the API, a local cache of all possible search terms is maintained in Cloud Storage bucket. This cache is refreshed periodically.


**Note:** The API is undocumented and may cease to work in the future!


Hosted on Google App Engine.


## Running locally
Install Python packages with  
```
pip install -r requirements.txt
```  
Then, run in localhost with
```
python main.py
```

## Unit tests
Unit tests can be run from the root folder with
```
pytest
```

## Deploy to Google App Engine
To deploy as an App Engine service, install the [gcloud CLI tool](https://cloud.google.com/sdk/gcloud) and run
```
gcloud app deploy
```
This does not deploy scheduling from `cron.yaml`. To do that, run
```
gcloud app deploy cron.yaml
```
Note that scheduling is App Engine specific and will overwerite any existing scheduling.
