
Planner_Agent = """Your task is to provide the steps for solving a multi-hop search problem. 

The output format should be: 
<think>: {Overall thought process} </think>\n <search> [{\"query\": \"{query}\", \"intent\": 1}]" </search>
query should be in sentence format.

Here are some examples:

Question: What is the undergraduate school of the director of the movie "Sense and Sensibility"?
Thought: <think> To answer this question, I will take the following steps:
1. First, find out who directed the movie "Sense and Sensibility".
2. Investigate the educational background of the director, particularly their undergraduate school.
3. Identify the specific institution where the director completed their undergraduate studies.
Now, I will start with the first step and search for the director of the movie "Sense and Sensibility". </think>
<search> [{"query": "Who is the director of the movie ’Sense and Sensibility’?", "intent": 1}]
</search>

Question: When did the birthplace of the performer of Live and Beyond become the capital of the state where Knowles is located?
Thought: <think> To determine when the birthplace of the performer of Live and Beyond
became the capital of the state where Knowles is located, I will take the following steps:
1. First, identify who the performer of Live and Beyond is.
2. Then find out the birthplace of this performer.
3. Next, search for which state Knowles is from.
4. Finally, determine when the birth city of the performer of Live and Beyond became the capital of Knowles’ state.
Now, I will start with the first step and search online to determine who the performer of Live and
Beyond is. </think>
<search> [{"query": "Find out who the performer of Live and Beyond is", "intent": 1}]
</search>


Question: {input}
"""


Searcher_Agent = """
Given a piece of content containing SUBQUERIES to search, rewrite the SUBQUERIES in order to obtain more comprehensive search results. Please provide at least three rewritten queries.

The output format should be the following JSON structure:  
`{"queries": ["query 1", "query 2"]}`

Here are some examples:

**Content:**  
<think> To find out which undergraduate school the director of the movie "Sense and
Sensibility" attended, I will take the following steps:
1. First, determine who the director of the movie "Sense and Sensibility" is.
2. Then, search for educational background of this director, particularly undergraduate education.
Now, I’ll proceed with the first step by using online searches to identify the director of the movie "Sense and Sensibility". </think>
<search> [{"query": "Find out who the director of the movie ’Sense and Sensibility’ is",
"intent": 1}] </search>

**Rewritten Queries:**  
{"queries": ["Sense and Sensibility director", "Sense and Sensibility 1995 director", "Sense and Sensibility Filmmaker"]}

**Content:**  
<think> After analyzing the search results in detail, I concluded that the director of the movie "Sense and Sensibility" is Ang Lee. Therefore, I will proceed with the next step, where I need to search for his detailed undergraduate education. </think>
<search> [{"query": "Search for the undergraduate school of Ang Lee", "intent": 1}]
</search>

**Rewritten Queries:**  
{"queries": ["Ang Lee education background", "Ang Lee undergraduate school", "Ang Lee biography"]}

**Content:**  
{input}

**Rewritten Queries:**  """



Observation_Agent = """
Given a multi-hop search problem, the steps already taken, and the search results obtained from the last executed step, your task is to:

1. Carefully analyze the search results to determine if they resolve the previous step, and provide a summary.
2. Update the execution steps and propose new steps based on the search results. You may encounter the following scenarios:
    a. If the current search results are sufficient to arrive at the Final Answer to the problem, provide the final answer directly. Use the format: "<think> {thought process} </think> <answer> {answer} </answer> ". Please strictly adhere to this format.
    b. If the current search results resolve the previous step, proceed according to the original plan and provide the next new step. Use the format: "<think> {thought process} </think> <search> [{"query": "query", "intent": 1}] </search> "; the query should be in sentence format.
    c. If the current search results do not resolve the previous step, reflect on and update the previous execution steps based on the search results. Use the format: "<think> {reflection} </think> <search> [{"query": "query", "intent": 1}] </search> "; the query should be in sentence format.
    d. If after multiple reflections (at least twice), the search still fails to resolve the issue, supplement based on your knowledge and provide the next new step. Use the format: "<think> {thought process} </think> <search> [{"query": "query", "intent": 1}] </search> "; the query should be in sentence format.

Below are some examples:

Question: What is the undergraduate school of the director of the movie "Sense and Sensibility"?
Thought: <think> To find out the undergraduate school of the director of the movie "Sense and Sensibility", I will take the following steps:\\1. First, determine who directed the movie "Sense and Sensibility". \\2. Then, search for this director’s educational background, focusing on undergraduate education. \\I will now begin with step one by searching online to identify the director of the movie "Sense and Sensibility". </think>
<search> [{"query": "Find out who directed the movie 'Sense and Sensibility'", "intent": 1}] </search>
Observation: <information>
1. The movie "Sense and Sensibility" was released in 1995 and is directed by Ang Lee, a renowned director known for his work in both Eastern and Western cinema.
2. Ang Lee is recognized for directing major films such as "Crouching Tiger, Hidden Dragon" and "Life of Pi".
3. Ang Lee's background in filmmaking and storytelling has earned him multiple Academy Awards and international acclaim.
</information>
Thought: <think> After a detailed analysis of the search results, I concluded that Ang Lee is the director of the movie "Sense and Sensibility". Thus, I will proceed to the next step and search for Ang Lee’s educational background, focusing on his undergraduate education. </think>
<search> [{"query": "Search for the undergraduate school of Ang Lee", "intent": 1}] </search>



Question: What is the undergraduate school of the director of the movie "Sense and Sensibility"?
Thought: <think> To find out the undergraduate school of the director of the movie "Sense and Sensibility", I will take the following steps:\\1. First, determine who directed the movie "Sense and Sensibility". \\2. Then, search for this director’s educational background, focusing on undergraduate education. \\I will now begin with step one by searching online to identify the director of the movie "Sense and Sensibility". </think>
<search> [{"query": "Find out who directed the movie "Sense and Sensibility", "intent": 1}] </search>
Thought: <think> After a detailed analysis of the search results, I concluded that Ang Lee is the director of the movie "Sense and Sensibility". Thus, I will proceed to the next step and search for Ang Lee’s educational background, focusing on his undergraduate education. </think>
<search> [{"query": "Search for the undergraduate school of Ang Lee", "intent": 1}] </search>
Observation: <information>
1. Ang Lee graduated from the National Taiwan College of Arts in 1975 and then came to the U.S. to receive a B.F.A. Degree in Theatre/Theater Direction at the University of Illinois at Urbana-Champaign, and a Masters Degree in Film Production at New York University.
2. After high school Lee attended the Taiwan Academy of Art, where he became interested in acting. He moved to the United States in 1978 to study theater at the University of Illinois at Urbana-Champaign.
Thought: <think> After a thorough analysis of the search results, I found out that Ang Lee graduated from the National Taiwan University with a degree in French literature, as well as a B.F.A. Degree from the University of Illinois at Urbana-Champaign, therefore, the answer is </think> <answer> National Taiwan College of Arts and University of Illinois at Urbana-Champaign. </answer>



Question: Who is the director of the suspense drama that premiered on MBC?
Thought: <think> To solve this problem, I need to follow a few steps in my search: \n\nFirst, I need to identify which suspense drama premiered on MBC.\nThen, I will look up who directed that suspense drama.\nFirst, I will search for recent suspense dramas that premiered on MBC.</think>
<search> [{ "query": "What recent suspense dramas premiered on MBC?", "intent": 1}] </search>
Observation: <information>
1. Premiering soon! A 12-episode suspense drama is coming, starring Wang Zhiwen and Yu Ai... From the trailer, 'The Vanishing Elephant' combines suspense and comedy, bringing an amusing story with humor and absurdity."
2. Chen Weiting's suspense drama is airing, featuring time travel and criminal investigation, with top actors like award-winning actors joining."
3. The best 10 suspense dramas of the past 4 years, with 'The Big Squad' at the bottom. Though the series is framed as a historical drama, it unfolds as a large-scale suspense espionage drama."
4. Premiering soon! An 18-episode suspense drama is coming, starring Sun Li, with a strong cast. However, recent suspense dramas such as 'Dim Flames' and 'Rebirth' have not been well-received."
5. Lee Jong-suk's return! New drama 'The Black Lawyer' premiered on MBC, achieving high viewership. The story is a suspenseful crime drama about a vulnerable lawyer who is framed and battles powerful forces."
6. The top 10 suspense dramas to watch in 2024, featuring leading actors like Liao Fan, Duan Yihong, and Zhang Songwen..."
7. Premiering tonight! Another suspenseful drama is coming! 'Thirteen Years in Dust' will air on iQIYI's Mist Theater, starring Chen Jianbin and Chen Xiao."
8. Chen Weiting's new drama 'The Sun and Stars' debuted with impressive suspenseful plotlines.
</information>
Thought: <think> From the search results, I found several relevant pieces of information:\n1. The suspense drama 'The Black Lawyer' premiered on MBC, starring Lee Jong-suk and Im Yoon-ah, and it is a crime suspense drama. 2. The premiere of 'The Black Lawyer' achieved high ratings, telling a story about a vulnerable lawyer who is framed and fights back against powerful figures. 3. However, the search results did not provide the director's information for 'The Black Lawyer.' \nFilter out unrelated content: The search results also mention suspense dramas on other platforms like iQIYI and Mist Theater, and other non-MBC dramas, such as 'The Sun and Stars.' These are not directly related to the question and can be excluded. \nCurrent progress summary: Based on the retrieved information, 'The Black Lawyer' is a recent suspense drama premiered on MBC, but the director’s information is still missing. \nNext plan: I will continue with the second step of my plan, searching for the director of 'The Black Lawyer.' </think>
<search> [{"query": "Who is the director of 'The Black Lawyer'?", "intent": 1}] </search>


Question: {input}
{Thought}
Observation: {Observation}
"""
