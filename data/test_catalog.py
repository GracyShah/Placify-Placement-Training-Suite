TOPIC_TEST_BLUEPRINTS = {
    "Aptitude": {
        "description": "Quantitative aptitude practice focused on arithmetic, percentages, ratios, and data interpretation.",
        "time_limit": 18,
        "test_count": 7,
        "question_indexes": [
            [0, 1, 2, 3, 4],
            [1, 3, 5, 6, 7],
            [0, 2, 4, 6, 8],
            [1, 2, 5, 7, 9],
            [0, 3, 4, 8, 9],
            [2, 4, 5, 6, 9],
            [0, 1, 7, 8, 9],
        ],
        "bank": [
            {
                "question_key": "apt-q1",
                "question_text": "A student buys a book for Rs.480 after a 20% discount. What was the marked price?",
                "options": {"A": "Rs.560", "B": "Rs.575", "C": "Rs.600", "D": "Rs.625"},
                "correct_answer": "C",
                "explanation": "If 80% of the marked price is 480, then the marked price is 480 / 0.8 = 600.",
            },
            {
                "question_key": "apt-q2",
                "question_text": "The ratio of boys to girls in a class is 7:5. If there are 48 students, how many are girls?",
                "options": {"A": "18", "B": "20", "C": "22", "D": "24"},
                "correct_answer": "B",
                "explanation": "Total ratio parts = 12. Each part = 48 / 12 = 4, so girls = 5 x 4 = 20.",
            },
            {
                "question_key": "apt-q3",
                "question_text": "A train running at 72 km/h crosses a pole in 15 seconds. What is the length of the train?",
                "options": {"A": "250 m", "B": "275 m", "C": "300 m", "D": "320 m"},
                "correct_answer": "C",
                "explanation": "72 km/h = 20 m/s. Length = speed x time = 20 x 15 = 300 m.",
            },
            {
                "question_key": "apt-q4",
                "question_text": "If the average of 8 numbers is 24, what is the total of the numbers?",
                "options": {"A": "168", "B": "176", "C": "184", "D": "192"},
                "correct_answer": "D",
                "explanation": "Sum = average x count = 24 x 8 = 192.",
            },
            {
                "question_key": "apt-q5",
                "question_text": "A sum becomes Rs.12,000 at 10% simple interest in 2 years. What is the principal?",
                "options": {"A": "Rs.10,000", "B": "Rs.10,500", "C": "Rs.11,000", "D": "Rs.11,500"},
                "correct_answer": "A",
                "explanation": "Amount = P(1 + 10 x 2 / 100) = 1.2P, so P = 12000 / 1.2 = 10000.",
            },
            {
                "question_key": "apt-q6",
                "question_text": "A shopkeeper gains 25% after selling an item for Rs.1,000. What is the cost price?",
                "options": {"A": "Rs.750", "B": "Rs.800", "C": "Rs.825", "D": "Rs.850"},
                "correct_answer": "B",
                "explanation": "Selling price = 125% of cost price. Cost price = 1000 / 1.25 = 800.",
            },
            {
                "question_key": "apt-q7",
                "question_text": "Pipe A fills a tank in 12 hours and Pipe B fills it in 18 hours. How long will they take together?",
                "options": {"A": "6.2 hours", "B": "7.2 hours", "C": "7.5 hours", "D": "8 hours"},
                "correct_answer": "B",
                "explanation": "Combined rate = 1/12 + 1/18 = 5/36, so time = 36/5 = 7.2 hours.",
            },
            {
                "question_key": "apt-q8",
                "question_text": "What is the next number in the series 3, 6, 12, 24, 48, ?",
                "options": {"A": "72", "B": "84", "C": "96", "D": "108"},
                "correct_answer": "C",
                "explanation": "Each term is doubled, so the next term is 96.",
            },
            {
                "question_key": "apt-q9",
                "question_text": "If 40% of a number is 84, what is 65% of that number?",
                "options": {"A": "126", "B": "132", "C": "136.5", "D": "140"},
                "correct_answer": "C",
                "explanation": "Number = 84 / 0.4 = 210. Then 65% of 210 is 136.5.",
            },
            {
                "question_key": "apt-q10",
                "question_text": "A can finish a task in 15 days and B can finish it in 10 days. How many days will they take together?",
                "options": {"A": "5", "B": "6", "C": "7.5", "D": "8"},
                "correct_answer": "B",
                "explanation": "Combined rate = 1/15 + 1/10 = 1/6, so they take 6 days.",
            },
        ],
    },
    "Logical": {
        "description": "Logical reasoning practice built around arrangements, coding-decoding, syllogisms, and patterns.",
        "time_limit": 18,
        "test_count": 6,
        "question_indexes": [
            [0, 1, 2, 3, 4],
            [1, 3, 5, 6, 7],
            [0, 2, 4, 6, 8],
            [1, 2, 5, 7, 9],
            [0, 3, 4, 8, 9],
            [2, 4, 5, 6, 9],
        ],
        "bank": [
            {
                "question_key": "log-q1",
                "question_text": "Complete the series: 5, 11, 23, 47, ?",
                "options": {"A": "88", "B": "90", "C": "95", "D": "99"},
                "correct_answer": "C",
                "explanation": "Each term is previous x 2 + 1, so 47 x 2 + 1 = 95.",
            },
            {
                "question_key": "log-q2",
                "question_text": "If in a code TABLE is written as UBCMF, how is CHAIR written?",
                "options": {"A": "DIBJS", "B": "DIBHQ", "C": "DJBJS", "D": "DHBJS"},
                "correct_answer": "A",
                "explanation": "Each letter is shifted one position ahead in the alphabet.",
            },
            {
                "question_key": "log-q3",
                "question_text": "All engineers are graduates. Some graduates are coders. Which conclusion is definitely true?",
                "options": {
                    "A": "All coders are engineers",
                    "B": "Some engineers are coders",
                    "C": "All engineers are graduates",
                    "D": "No graduate is a coder",
                },
                "correct_answer": "C",
                "explanation": "Only the first statement is guaranteed by the premise.",
            },
            {
                "question_key": "log-q4",
                "question_text": "P is east of Q. R is north of P. S is west of R. In which direction is S from Q?",
                "options": {"A": "North", "B": "North-East", "C": "South", "D": "West"},
                "correct_answer": "A",
                "explanation": "From Q move east to P, north to R, then west to S, landing directly north of Q.",
            },
            {
                "question_key": "log-q5",
                "question_text": "Find the odd one out: Square, Triangle, Circle, Rectangle",
                "options": {"A": "Square", "B": "Triangle", "C": "Circle", "D": "Rectangle"},
                "correct_answer": "C",
                "explanation": "Circle is the only figure without sides or vertices.",
            },
            {
                "question_key": "log-q6",
                "question_text": "A clock shows 3:15. What is the angle between the hour and minute hands?",
                "options": {"A": "0 degrees", "B": "7.5 degrees", "C": "15 degrees", "D": "22.5 degrees"},
                "correct_answer": "B",
                "explanation": "Hour hand = 97.5 degrees, minute hand = 90 degrees, difference = 7.5 degrees.",
            },
            {
                "question_key": "log-q7",
                "question_text": "If 1 = 3, 2 = 3, 3 = 5, 4 = 4, 5 = 4, then 6 = ?",
                "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                "correct_answer": "A",
                "explanation": "The value equals the number of letters in the word: six has 3 letters.",
            },
            {
                "question_key": "log-q8",
                "question_text": "Pointing to a woman, Ravi says, 'She is the daughter of my grandfather's only son.' How is the woman related to Ravi?",
                "options": {"A": "Sister", "B": "Cousin", "C": "Daughter", "D": "Niece"},
                "correct_answer": "A",
                "explanation": "Grandfather's only son is Ravi's father, so the woman is Ravi's sister.",
            },
            {
                "question_key": "log-q9",
                "question_text": "Choose the correct mirror image relationship for the pair: 12 : 21 :: 34 : ?",
                "options": {"A": "43", "B": "44", "C": "54", "D": "31"},
                "correct_answer": "A",
                "explanation": "The numbers are reversed in order.",
            },
            {
                "question_key": "log-q10",
                "question_text": "In a row of 40 students, Maya is 12th from the left and Nisha is 19th from the right. How many students are between them if Maya is to the left of Nisha?",
                "options": {"A": "7", "B": "8", "C": "9", "D": "10"},
                "correct_answer": "C",
                "explanation": "Nisha is 22nd from the left. Students between them = 22 - 12 - 1 = 9.",
            },
        ],
    },
    "Verbal": {
        "description": "Verbal ability practice covering grammar, vocabulary, sentence correction, and reading logic.",
        "time_limit": 16,
        "test_count": 5,
        "question_indexes": [
            [0, 1, 2, 3, 4],
            [1, 3, 5, 6, 7],
            [0, 2, 4, 6, 8],
            [1, 2, 5, 7, 9],
            [0, 3, 4, 8, 9],
        ],
        "bank": [
            {
                "question_key": "ver-q1",
                "question_text": "Choose the correctly spelled word.",
                "options": {"A": "Accomodate", "B": "Acommodate", "C": "Accommodate", "D": "Acomodate"},
                "correct_answer": "C",
                "explanation": "Accommodate has double c and double m.",
            },
            {
                "question_key": "ver-q2",
                "question_text": "Select the synonym of 'brief'.",
                "options": {"A": "Lengthy", "B": "Concise", "C": "Vague", "D": "Hidden"},
                "correct_answer": "B",
                "explanation": "Brief means short or concise.",
            },
            {
                "question_key": "ver-q3",
                "question_text": "Fill in the blank: She has been working here ___ 2019.",
                "options": {"A": "since", "B": "for", "C": "from", "D": "during"},
                "correct_answer": "A",
                "explanation": "Since is used with a starting point in time.",
            },
            {
                "question_key": "ver-q4",
                "question_text": "Choose the antonym of 'expand'.",
                "options": {"A": "stretch", "B": "shrink", "C": "extend", "D": "develop"},
                "correct_answer": "B",
                "explanation": "Shrink is the opposite of expand.",
            },
            {
                "question_key": "ver-q5",
                "question_text": "Identify the grammatically correct sentence.",
                "options": {
                    "A": "Neither of the answers are correct.",
                    "B": "Neither of the answers is correct.",
                    "C": "Neither of the answer is correct.",
                    "D": "Neither of answer are correct.",
                },
                "correct_answer": "B",
                "explanation": "Neither takes a singular verb here, so 'is' is correct.",
            },
            {
                "question_key": "ver-q6",
                "question_text": "Choose the word that best completes the sentence: The manager appreciated her ___ response to the issue.",
                "options": {"A": "prompt", "B": "delayed", "C": "casual", "D": "silent"},
                "correct_answer": "A",
                "explanation": "Prompt means quick and timely, which best fits the sentence.",
            },
            {
                "question_key": "ver-q7",
                "question_text": "Select the sentence with correct punctuation.",
                "options": {
                    "A": "However I decided to continue.",
                    "B": "However, I decided to continue.",
                    "C": "However I, decided to continue.",
                    "D": "However; I decided, to continue.",
                },
                "correct_answer": "B",
                "explanation": "A comma is needed after the introductory adverb 'However'.",
            },
            {
                "question_key": "ver-q8",
                "question_text": "Choose the correct meaning of the idiom 'hit the books'.",
                "options": {"A": "to damage books", "B": "to study seriously", "C": "to write a book", "D": "to buy books"},
                "correct_answer": "B",
                "explanation": "The idiom means to begin studying with concentration.",
            },
            {
                "question_key": "ver-q9",
                "question_text": "Fill in the blank: If I ___ enough time, I would learn German.",
                "options": {"A": "have", "B": "had", "C": "will have", "D": "am having"},
                "correct_answer": "B",
                "explanation": "This is a second conditional sentence, so 'had' is correct.",
            },
            {
                "question_key": "ver-q10",
                "question_text": "Choose the sentence in active voice.",
                "options": {
                    "A": "The code was reviewed by Neha.",
                    "B": "The issue was solved yesterday.",
                    "C": "Neha reviewed the code.",
                    "D": "The task was completed by the team.",
                },
                "correct_answer": "C",
                "explanation": "Active voice places the doer before the verb: Neha reviewed the code.",
            },
        ],
    },
    "DSA Basics": {
        "description": "DSA basics practice around arrays, recursion, stacks, queues, complexity, and searching.",
        "time_limit": 20,
        "test_count": 7,
        "question_indexes": [
            [0, 1, 2, 3, 4],
            [1, 3, 5, 6, 7],
            [0, 2, 4, 6, 8],
            [1, 2, 5, 7, 9],
            [0, 3, 4, 8, 9],
            [2, 4, 5, 6, 9],
            [0, 1, 7, 8, 9],
        ],
        "bank": [
            {
                "question_key": "dsa-q1",
                "question_text": "What is the time complexity of binary search on a sorted array?",
                "options": {"A": "O(n)", "B": "O(log n)", "C": "O(n log n)", "D": "O(1)"},
                "correct_answer": "B",
                "explanation": "Binary search halves the search space each step.",
            },
            {
                "question_key": "dsa-q2",
                "question_text": "Which data structure follows the FIFO principle?",
                "options": {"A": "Stack", "B": "Queue", "C": "Heap", "D": "Tree"},
                "correct_answer": "B",
                "explanation": "Queue is first in, first out.",
            },
            {
                "question_key": "dsa-q3",
                "question_text": "Which traversal of a BST gives values in sorted order?",
                "options": {"A": "Preorder", "B": "Postorder", "C": "Inorder", "D": "Level order"},
                "correct_answer": "C",
                "explanation": "Inorder traversal of a BST returns keys in increasing order.",
            },
            {
                "question_key": "dsa-q4",
                "question_text": "What is the worst-case time complexity of bubble sort?",
                "options": {"A": "O(n)", "B": "O(log n)", "C": "O(n log n)", "D": "O(n^2)"},
                "correct_answer": "D",
                "explanation": "Bubble sort performs nested passes in the worst case.",
            },
            {
                "question_key": "dsa-q5",
                "question_text": "Which data structure is typically used to implement recursion internally?",
                "options": {"A": "Queue", "B": "Stack", "C": "Hash map", "D": "Graph"},
                "correct_answer": "B",
                "explanation": "Recursive calls are managed on the call stack.",
            },
            {
                "question_key": "dsa-q6",
                "question_text": "What does hashing primarily help optimize?",
                "options": {"A": "Sequential traversal", "B": "Fast average-case lookup", "C": "Sorting speed only", "D": "Graph drawing"},
                "correct_answer": "B",
                "explanation": "Hashing is used for efficient average-case search and insert operations.",
            },
            {
                "question_key": "dsa-q7",
                "question_text": "Which of these is not a linear data structure?",
                "options": {"A": "Array", "B": "Linked List", "C": "Queue", "D": "Tree"},
                "correct_answer": "D",
                "explanation": "A tree is hierarchical, not linear.",
            },
            {
                "question_key": "dsa-q8",
                "question_text": "In an array of n elements, what is the index of the last element?",
                "options": {"A": "n", "B": "n + 1", "C": "n - 1", "D": "1"},
                "correct_answer": "C",
                "explanation": "Array indexing starts at 0 in common programming languages.",
            },
            {
                "question_key": "dsa-q9",
                "question_text": "Which algorithmic technique breaks a problem into overlapping subproblems and stores results?",
                "options": {"A": "Greedy", "B": "Backtracking", "C": "Dynamic Programming", "D": "Branch and Bound"},
                "correct_answer": "C",
                "explanation": "Dynamic programming stores results of overlapping subproblems.",
            },
            {
                "question_key": "dsa-q10",
                "question_text": "In a max-heap, the root node contains:",
                "options": {"A": "smallest element", "B": "median element", "C": "largest element", "D": "random element"},
                "correct_answer": "C",
                "explanation": "Max-heaps keep the maximum at the root.",
            },
        ],
    },
    "SQL": {
        "description": "SQL fundamentals practice on joins, grouping, filtering, aggregates, and normalization basics.",
        "time_limit": 18,
        "test_count": 6,
        "question_indexes": [
            [0, 1, 2, 3, 4],
            [1, 3, 5, 6, 7],
            [0, 2, 4, 6, 8],
            [1, 2, 5, 7, 9],
            [0, 3, 4, 8, 9],
            [2, 4, 5, 6, 9],
        ],
        "bank": [
            {
                "question_key": "sql-q1",
                "question_text": "Which SQL clause is used to filter rows after aggregation?",
                "options": {"A": "WHERE", "B": "ORDER BY", "C": "HAVING", "D": "GROUP BY"},
                "correct_answer": "C",
                "explanation": "HAVING filters grouped results after aggregate functions are applied.",
            },
            {
                "question_key": "sql-q2",
                "question_text": "Which join returns only matching rows from both tables?",
                "options": {"A": "LEFT JOIN", "B": "INNER JOIN", "C": "RIGHT JOIN", "D": "FULL JOIN"},
                "correct_answer": "B",
                "explanation": "INNER JOIN keeps only rows with matches in both tables.",
            },
            {
                "question_key": "sql-q3",
                "question_text": "What does COUNT(*) return?",
                "options": {"A": "Only non-null rows", "B": "Only distinct rows", "C": "All rows", "D": "Only rows with numeric data"},
                "correct_answer": "C",
                "explanation": "COUNT(*) counts every row in the result set.",
            },
            {
                "question_key": "sql-q4",
                "question_text": "Which command removes all rows from a table but keeps the table structure?",
                "options": {"A": "DROP TABLE", "B": "DELETE TABLE", "C": "TRUNCATE TABLE", "D": "REMOVE ALL"},
                "correct_answer": "C",
                "explanation": "TRUNCATE removes rows while retaining the table definition.",
            },
            {
                "question_key": "sql-q5",
                "question_text": "Which keyword is used to sort query results in descending order?",
                "options": {"A": "SORT DESC", "B": "GROUP DESC", "C": "ORDER BY ... DESC", "D": "DESCENDING"},
                "correct_answer": "C",
                "explanation": "SQL uses ORDER BY column DESC for descending sort.",
            },
            {
                "question_key": "sql-q6",
                "question_text": "Which normal form removes partial dependency on a composite key?",
                "options": {"A": "1NF", "B": "2NF", "C": "3NF", "D": "BCNF"},
                "correct_answer": "B",
                "explanation": "Second Normal Form removes partial dependency.",
            },
            {
                "question_key": "sql-q7",
                "question_text": "Which operator is used to search for a pattern in SQL?",
                "options": {"A": "MATCH", "B": "FIND", "C": "SEARCH", "D": "LIKE"},
                "correct_answer": "D",
                "explanation": "LIKE is used with wildcards for pattern matching.",
            },
            {
                "question_key": "sql-q8",
                "question_text": "Which statement updates existing records in a table?",
                "options": {"A": "MODIFY", "B": "UPDATE", "C": "ALTER", "D": "CHANGE"},
                "correct_answer": "B",
                "explanation": "UPDATE modifies existing table rows.",
            },
            {
                "question_key": "sql-q9",
                "question_text": "What is the purpose of a PRIMARY KEY?",
                "options": {"A": "To sort data", "B": "To uniquely identify each row", "C": "To duplicate rows", "D": "To encrypt data"},
                "correct_answer": "B",
                "explanation": "A primary key uniquely identifies each record.",
            },
            {
                "question_key": "sql-q10",
                "question_text": "Which aggregate function returns the highest value in a column?",
                "options": {"A": "TOP()", "B": "HIGH()", "C": "MAX()", "D": "UPPER()"},
                "correct_answer": "C",
                "explanation": "MAX() returns the largest value.",
            },
        ],
    },
}


COMPANY_TEST_SEED = {
    "amazon": {
        "test_name": "Amazon Online Assessment – Full Placement Test",
        "questions": [
            ("Aptitude", "What is 25% of 640?", {"A": "120", "B": "140", "C": "160", "D": "180"}, "C", "25% of 640 is 160."),
            ("Logical", "If CLOUD is coded as 59413, what is COULD?", {"A": "59314", "B": "59431", "C": "59413", "D": "53914"}, "B", "Rearrange the mapped letters to match COULD."),
            ("Verbal", "Choose the correct sentence.", {"A": "Each of the students have submitted.", "B": "Each of the students has submitted.", "C": "Each students has submitted.", "D": "Each student have submitted."}, "B", "Each takes a singular verb."),
            ("DSA Basics", "Which data structure is ideal for DFS?", {"A": "Queue", "B": "Stack", "C": "Heap", "D": "Trie"}, "B", "Depth-first traversal uses a stack."),
            ("SQL", "Which clause is used to combine rows with the same values?", {"A": "ORDER BY", "B": "HAVING", "C": "GROUP BY", "D": "UNION"}, "C", "GROUP BY groups rows for aggregation."),
            ("Aptitude", "A number is increased by 20% and then decreased by 20%. What is the net change?", {"A": "No change", "B": "4% decrease", "C": "4% increase", "D": "2% decrease"}, "B", "1.2 x 0.8 = 0.96, so net 4% decrease."),
            ("Logical", "Find the odd one out: API, SDK, JSON, Banana", {"A": "API", "B": "SDK", "C": "JSON", "D": "Banana"}, "D", "Banana is unrelated."),
            ("Verbal", "Choose the synonym of 'robust'.", {"A": "fragile", "B": "strong", "C": "brief", "D": "silent"}, "B", "Robust means strong."),
            ("DSA Basics", "Average-case lookup in a hash table is typically:", {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n log n)"}, "A", "Hash tables target constant average-time lookup."),
            ("SQL", "Which query returns unique values?", {"A": "SELECT UNIQUE", "B": "SELECT ONLY", "C": "SELECT DISTINCT", "D": "SELECT FILTER"}, "C", "DISTINCT removes duplicates."),
        ],
    },
    "tcs": {
        "test_name": "TCS NQT – Complete Mock Test",
        "questions": [
            ("Aptitude", "If 18 men can complete a work in 24 days, how many men are needed to finish it in 12 days?", {"A": "24", "B": "30", "C": "36", "D": "42"}, "C", "Work is constant, so men x days = 432. 432 / 12 = 36."),
            ("Logical", "Series: 1, 4, 9, 16, ?", {"A": "20", "B": "24", "C": "25", "D": "36"}, "C", "These are squares: 1, 2, 3, 4, so next is 5^2."),
            ("Verbal", "Fill in the blank: He insisted ___ paying the bill.", {"A": "for", "B": "on", "C": "at", "D": "to"}, "B", "The correct usage is insisted on."),
            ("DSA Basics", "Which structure is used for BFS in graphs?", {"A": "Stack", "B": "Queue", "C": "Array", "D": "Hash map"}, "B", "Breadth-first search uses a queue."),
            ("SQL", "Which command adds a new column to an existing table?", {"A": "UPDATE TABLE", "B": "CHANGE TABLE", "C": "ALTER TABLE", "D": "MODIFY TABLE"}, "C", "ALTER TABLE is used to change table structure."),
            ("Aptitude", "Simple interest on Rs.5000 at 8% per annum for 2 years is:", {"A": "Rs.400", "B": "Rs.600", "C": "Rs.800", "D": "Rs.1000"}, "C", "SI = PRT/100 = 5000 x 8 x 2 / 100 = 800."),
            ("Logical", "Pointing to a photograph, Mira says, 'He is my mother's only brother's son.' How is the person related to Mira?", {"A": "Brother", "B": "Cousin", "C": "Uncle", "D": "Nephew"}, "B", "Mother's brother's son is a cousin."),
            ("Verbal", "Choose the antonym of 'optimistic'.", {"A": "hopeful", "B": "confident", "C": "pessimistic", "D": "calm"}, "C", "Pessimistic is the opposite."),
            ("DSA Basics", "The worst-case complexity of linear search is:", {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n log n)"}, "C", "It may inspect every element."),
            ("SQL", "Which function returns the total of numeric values?", {"A": "COUNT()", "B": "TOTAL()", "C": "AVG()", "D": "SUM()"}, "D", "SUM() adds numeric values."),
        ],
    },
    "infosys": {
        "test_name": "Infosys Certified Specialist Exam",
        "questions": [
            ("Aptitude", "A car covers 180 km in 3 hours. What is its speed?", {"A": "45 km/h", "B": "50 km/h", "C": "55 km/h", "D": "60 km/h"}, "D", "Speed = distance / time = 180 / 3."),
            ("Logical", "Choose the missing term: AZ, BY, CX, ?", {"A": "DV", "B": "DW", "C": "EV", "D": "EW"}, "B", "The first letter increases, second decreases: A-Z, B-Y, C-X, D-W."),
            ("Verbal", "Choose the correctly ordered sentence: 'rarely / errors / production / in / unnoticed / go'", {"A": "Errors go unnoticed in production rarely.", "B": "Rarely errors go unnoticed in production.", "C": "Errors rarely go unnoticed in production.", "D": "In production go unnoticed errors rarely."}, "C", "This is the natural and grammatically correct order."),
            ("DSA Basics", "Which sorting algorithm divides the array and merges sorted halves?", {"A": "Bubble sort", "B": "Merge sort", "C": "Selection sort", "D": "Insertion sort"}, "B", "Merge sort uses divide and conquer."),
            ("SQL", "Which statement is used to remove specific rows from a table?", {"A": "REMOVE", "B": "DELETE", "C": "DROP", "D": "TRUNCATE"}, "B", "DELETE removes selected rows."),
            ("Aptitude", "The average of 5 numbers is 18. If four numbers are 14, 16, 18, and 20, the fifth number is:", {"A": "20", "B": "22", "C": "24", "D": "26"}, "B", "Total is 90. Known sum is 68, so the fifth number is 22."),
            ("Logical", "If all pens are tools and some tools are expensive, which statement is certain?", {"A": "All tools are pens", "B": "Some pens are expensive", "C": "All pens are tools", "D": "No pen is expensive"}, "C", "Only the first relation is guaranteed."),
            ("Verbal", "Choose the word closest in meaning to 'meticulous'.", {"A": "careless", "B": "precise", "C": "quick", "D": "ordinary"}, "B", "Meticulous means very careful and precise."),
            ("DSA Basics", "In a max-heap, the root node contains:", {"A": "smallest element", "B": "median element", "C": "largest element", "D": "random element"}, "C", "Max-heaps keep the maximum at the root."),
            ("SQL", "Which clause is evaluated first in a simple SELECT query?", {"A": "SELECT", "B": "ORDER BY", "C": "FROM", "D": "HAVING"}, "C", "Logically, SQL starts from FROM before filtering and projecting."),
        ],
    },
}


def build_topic_test_catalog():
    catalog = []
    for topic_name, config in TOPIC_TEST_BLUEPRINTS.items():
        tests = []
        for test_number, indexes in enumerate(config["question_indexes"], start=1):
            questions = []
            for order, question_index in enumerate(indexes, start=1):
                question = config["bank"][question_index]
                questions.append(
                    {
                        "question_id": f"{topic_name.lower().replace(' ', '-')}-test-{test_number}-q{order}",
                        "question_key": question["question_key"],
                        "question_text": question["question_text"],
                        "options": question["options"],
                        "correct_answer": question["correct_answer"],
                        "explanation": question["explanation"],
                        "points": 1,
                    }
                )

            tests.append(
                {
                    "test_id": f"{topic_name.lower().replace(' ', '-')}-test-{test_number}",
                    "topic_name": topic_name,
                    "test_name": f"{topic_name} Test {test_number}",
                    "description": f"{topic_name} fixed practice set {test_number}.",
                    "time_limit": config["time_limit"],
                    "questions": questions,
                }
            )

        catalog.append(
            {
                "topic_name": topic_name,
                "description": config["description"],
                "test_count": config["test_count"],
                "tests": tests,
            }
        )
    return catalog


TOPIC_TEST_CATALOG = build_topic_test_catalog()
