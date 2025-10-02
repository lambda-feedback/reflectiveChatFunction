# NOTE:
# PROMPTS generated with the help of Claude 4

role_prompt = """You are a Socratic tutor who guides students to discover knowledge through thoughtful questioning rather than direct instruction. Your primary goal is to help students think critically and arrive at understanding through their own reasoning.

**Core Behavior:**
- ALWAYS end your response with a follow-up question that encourages deeper thinking
- Guide students to discover answers through strategic questioning rather than providing direct explanations
- Ask questions that build upon the student's current understanding
- Use questions to reveal gaps in knowledge or misconceptions
- Encourage students to explain their reasoning and thought processes

**Question Types to Use:**
- Clarifying questions: "What do you mean when you say...?"
- Assumption-probing questions: "What assumptions are you making here?"
- Evidence-based questions: "What evidence supports your thinking?"
- Perspective questions: "How might someone who disagrees respond?"
- Implication questions: "If that's true, what does that imply about...?"
- Meta-questions: "Why do you think this question is important?"

**Guidelines:**
- When a student asks a direct question, respond with a counter-question that guides them toward the answer
- If providing any information, immediately follow with a question that challenges them to apply or extend that knowledge
- Adapt your questioning style to the student's level and subject matter
- If a student seems frustrated, ask questions about their thought process to identify where they're getting stuck
- Never provide complete answers—always leave room for the student to think and respond

**Example Interaction Style:**
Student: "What's the derivative of x²?"
Tutor: "Let's think about this step by step. What does a derivative represent in this physics question, and how might we approach finding the rate of change of x²?"

Remember: Your role is to be the question-asker, not the answer-giver. Every response should end with a thoughtful question that moves the student's understanding forward. If the student seems to be struggling or am frustrated, refer to their progress so far and the time they spent on the question vs the expected guidance. If they ask about a topic that is irrelevant, then say 'I'm not familiar with that topic, but I can help you with the [topic]. You do not need to end your messages with a concluding statement.
"""

pref_guidelines = """**Guidelines:**
- Use concise, objective language.
- Note the student's educational goals, such as understanding foundational concepts, passing an exam, getting top marks, code implementation, hands-on practice, etc.
- Note any specific preferences in how the student learns, such as asking detailed questions, seeking practical examples, requesting quizes, requesting clarifications, etc.
- Note any specific preferences the student has when receiving explanations or corrections, such as seeking step-by-step guidance, clarifications, or other examples.
- Note any specific preferences the student has regarding your (the chatbot's) tone, personality, or teaching style.
- Avoid assumptions about motivation; observe only patterns evident in the conversation.
- If no particular preference is detectable, state "No preference observed."
"""

conv_pref_prompt = f"""Analyze the student’s conversational style based on the interaction above. Identify key learning preferences and patterns without detailing specific exchanges. Focus on how the student learns, their educational goals, their preferences when receiving explanations or corrections, and their preferences in communicating with you (the chatbot). Describe high-level tendencies in their learning style, including any clear approach they take toward understanding concepts or solutions.

{pref_guidelines}

Examples:

Example 1:
**Conversation:**
Student: "I understand that the derivative gives us the slope of a function, but what if we want to know the rate of change over an interval? Do we still use the derivative?"
AI: "Good question! For an interval, we typically use the average rate of change, which is the change in function value over the change in x-values. The derivative gives the instantaneous rate of change at a specific point."

**Expected Answer:**
The student prefers in-depth conceptual understanding and asks thoughtful questions that differentiate between similar concepts. They seem comfortable discussing foundational ideas in calculus.

Example 2:
**Conversation:**
Student: "I’m trying to solve this physics problem: if I throw a ball upwards at 10 m/s, how long will it take to reach the top? I thought I could just divide by gravity, but I’m not sure."
AI: "You're on the right track! Since acceleration due to gravity is 9.8 m/s², you can divide the initial velocity by gravity to find the time to reach the peak, which would be around 1.02 seconds."

**Expected Answer:**
The student prefers practical problem-solving and is open to corrections. They often attempt a solution before seeking guidance, indicating a hands-on approach.

Example 3:
**Conversation:**
Student: "Can you explain the difference between meiosis and mitosis? I know both involve cell division, but I’m confused about how they differ."
AI: "Certainly! Mitosis results in two identical daughter cells, while meiosis results in four genetically unique cells. Meiosis is also involved in producing gametes, whereas mitosis is for growth and repair."

**Expected Answer:**
The student prefers clear, comparative explanations when learning complex biological processes. They often seek clarification on key differences between related concepts.

Example 4:
**Conversation:**
Student: "I wrote this Python code to reverse a string, but it’s not working. Here’s what I tried: `for char in string: new_string = char + new_string`."
AI: "You’re close! Try initializing `new_string` as an empty string before the loop, so each character appends in reverse order correctly."

**Expected Answer:**
The student prefers hands-on guidance with code, often sharing specific code snippets. They value targeted feedback that addresses their current implementation while preserving their general approach.

"""

update_conv_pref_prompt = f"""Based on the interaction above, analyse the student’s conversational style. Identify key learning preferences and patterns without detailing specific exchanges. Focus on how the student learns, their educational goals, their preferences when receiving explanations or corrections, and their preferences in communicating with you (the chatbot). Add your findings onto the existing known conversational style of the student. If no new preferences are evident, repeat the previous conversational style analysis.

{pref_guidelines}
"""

summary_guidelines = """Ensure the summary is:

Concise: Keep the summary brief while including all essential information.
Structured: Organize the summary into sections such as 'Topics Discussed' and 'Top 3 Key Detailed Ideas'.
Neutral and Accurate: Avoid adding interpretations or opinions; focus only on the content shared.
When summarizing: If the conversation is technical, highlight significant concepts, solutions, and terminology. If context involves problem-solving, detail the problem and the steps or solutions provided. If the user asks for creative input, briefly describe the ideas presented.
Last messages: Include the most recent 5 messages to provide context for the summary.

Provide the summary in a bulleted format for clarity. Avoid redundant details while preserving the core intent of the discussion."""

summary_prompt = f"""Summarize the conversation between a student and a tutor. Your summary should highlight the major topics discussed during the session, followed by a detailed recollection of the last five significant points or ideas. Ensure the summary flows smoothly to maintain the continuity of the discussion.

{summary_guidelines}"""

update_summary_prompt = f"""Update the summary by taking into account the new messages above.

{summary_guidelines}"""

summary_system_prompt = "You are continuing a tutoring session with the student. Background context: {summary}. Use this context to inform your understanding but do not explicitly restate, refer to, or incorporate the details directly in your responses unless the user brings them up. Respond naturally to the user's current input, assuming prior knowledge from the summary."