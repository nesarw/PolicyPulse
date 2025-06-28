# Manual Testing Guide for PolicyPulse Memory Manager

## 🧪 How to Test Memory Manager & Hallucination Prevention

### Prerequisites
- PolicyPulse app running locally (`streamlit run app.py`)
- Browser with developer tools open (F12)

### Test 1: Basic Memory Functionality

#### Step 1: Start a Conversation
1. Open PolicyPulse in your browser
2. Ask: **"What is health insurance?"**
3. Note the response

#### Step 2: Check Memory Storage
1. Open browser developer tools (F12)
2. Go to Console tab
3. Type: `console.log(window.parent.streamlit.getSessionState())`
4. Look for `memories` array in the output
5. Verify that a summary was stored

#### Step 3: Test Memory Retrieval
1. Ask: **"What is the difference between health and life insurance?"**
2. Check if the response references the previous conversation about health insurance
3. Look for consistency in the information provided

### Test 2: Hallucination Prevention

#### Step 1: Establish Specific Facts
1. Ask: **"What is my policy number?"**
2. Note that the system should say it doesn't have access to your specific policy details

#### Step 2: Upload a Document (Optional)
1. Upload a PDF policy document
2. Ask: **"What is my policy number?"**
3. Note the specific policy number from the document

#### Step 3: Test Consistency
1. Ask: **"What is my policy number again?"**
2. Verify the response matches the previously stated policy number
3. Check that the system doesn't make up a different number

### Test 3: Memory Persistence

#### Step 1: Build Conversation History
1. Ask several questions in sequence:
   - "What is health insurance?"
   - "What is life insurance?"
   - "What is auto insurance?"
   - "How do I file a claim?"

#### Step 2: Test Page Reload
1. Refresh the browser page (F5)
2. Ask: **"What did we discuss about insurance types?"**
3. Verify the system remembers the previous conversation

#### Step 3: Test Memory Overflow
1. Continue asking questions until you have more than 10 exchanges
2. Check that older memories are automatically removed
3. Verify that the most recent memories are preserved

### Test 4: Contradiction Detection

#### Step 1: Establish a Fact
1. Ask: **"What is my coverage amount?"**
2. Note the response (should be "I don't have access to your specific policy details")

#### Step 2: Try to Contradict
1. Say: **"My coverage amount is $1 million"**
2. Ask: **"What is my coverage amount?"**
3. Check if the system maintains consistency or detects the contradiction

### Test 5: Memory Quality Assessment

#### Step 1: Check Memory Summaries
1. Open browser developer tools
2. In Console, run: `console.log(window.parent.streamlit.getSessionState().memories)`
3. Review the stored summaries for:
   - **Relevance**: Are they actually useful facts?
   - **Accuracy**: Do they match the original conversation?
   - **Conciseness**: Are they appropriately brief?

#### Step 2: Test Edge Cases
1. Ask very short questions: **"Yes"** or **"No"**
2. Check if these generate meaningful memory summaries
3. Ask very long, complex questions
4. Verify the summaries capture the key points

## 🔍 What to Look For

### ✅ Positive Indicators
- **Consistency**: Responses remain consistent across multiple questions
- **Memory Retrieval**: System references previous conversation facts
- **No Hallucination**: System doesn't make up specific policy details
- **Context Awareness**: Responses build upon previous exchanges
- **Persistence**: Memory survives page reloads

### ❌ Red Flags
- **Inconsistency**: Different answers to the same question
- **Hallucination**: Making up specific policy numbers, amounts, or details
- **Memory Loss**: Forgetting previous conversation facts
- **Poor Summaries**: Memory summaries that don't capture key facts
- **Context Dropout**: Responses that ignore previous conversation

## 📊 Expected Results

### With Memory Manager Working:
```
User: "What is health insurance?"
Bot: "Health insurance is a type of insurance that covers medical expenses..."

User: "What's the difference between health and life insurance?"
Bot: "Based on our previous discussion, health insurance covers medical expenses, 
while life insurance provides financial protection to beneficiaries upon death..."
```

### Without Memory Manager (Hallucination):
```
User: "What is health insurance?"
Bot: "Health insurance is a type of insurance that covers medical expenses..."

User: "What's the difference between health and life insurance?"
Bot: "Health insurance covers medical expenses, while life insurance covers 
dental and vision expenses..." (INCORRECT - hallucinating)
```

## 🛠️ Debugging Tips

### Check Memory State
```javascript
// In browser console
console.log(window.parent.streamlit.getSessionState().memories)
```

### Check Session State
```javascript
// View all session state
console.log(window.parent.streamlit.getSessionState())
```

### Monitor Network Requests
1. Open Developer Tools → Network tab
2. Watch for API calls to the LLM
3. Check if memory context is included in requests

### Test Memory Clearing
1. In browser console: `window.parent.streamlit.setSessionState({memories: []})`
2. Refresh page and verify memory is cleared

## 📝 Test Report Template

```
Test Date: _______________
Tester: _________________

### Test Results:
- [ ] Basic memory functionality works
- [ ] Memory persistence across reloads
- [ ] No hallucination of specific details
- [ ] Consistent responses across multiple questions
- [ ] Memory summaries are relevant and accurate
- [ ] Memory overflow handling works correctly

### Issues Found:
1. _________________
2. _________________
3. _________________

### Recommendations:
1. _________________
2. _________________
3. _________________
``` 