# 🚀 Streamlit Testing Guide

**Business License Navigator - Web Interface Testing**

## 🌐 **Access the Application**

The Streamlit web interface is now running at:
**http://localhost:8502**

## 📋 **How to Test the Application**

### **1. Open the Web Interface**
1. Open your web browser
2. Navigate to: `http://localhost:8502`
3. You should see the Business License Navigator interface

### **2. Configure API Keys**
1. In the sidebar, enter your `GEMINI_API_KEY`
2. This enables full functionality with AI responses
3. Without an API key, you'll get limited functionality

### **3. Test the Ice Cream Franchise Scenario**

#### **Step 1: Use the Test Query**
1. In the sidebar, select the test query:
   ```
   "I want to open an ice cream franchise in FL for Rita's"
   ```
2. Click "🚀 Use Test Query"

#### **Step 2: Test Analysis**
1. Click "🧪 Test Analysis" to see the intelligent semantic search results
2. Verify that it detects:
   - Business Type: `food_hospitality`
   - Detected Licenses: 5 Florida licenses
   - Cost Estimate: $800-3500
   - Timeline: 4-8 weeks

#### **Step 3: Process the Query**
1. Click "🚀 Process Query" to get the full AI response
2. Check that the response includes:
   - License information
   - Source information (official Florida websites)
   - Cost breakdown
   - Next steps

### **4. Test Other Scenarios**

Try these additional test queries:

#### **Financial Services in Delaware**
```
"What licenses do I need for a financial services firm in Delaware?"
```

#### **Restaurant in California**
```
"How do I start a restaurant in California?"
```

#### **Construction Company in Texas**
```
"What are the requirements for a construction company in Texas?"
```

## 🧪 **Acceptance Criteria Verification**

### **✅ Test Each Criterion:**

1. **Query Processing** ✅
   - Enter: "I want to open an ice cream franchise in FL for Rita's"
   - Verify: Business type detected as `food_hospitality`

2. **Fetch and Playwright Integration** ✅
   - Verify: MCP servers are available in system status
   - Check: Response includes source information

3. **Augmented Prompt Creation** ✅
   - Use "Test Analysis" feature
   - Verify: Comprehensive prompt with business analysis

4. **Source Information Display** ✅
   - Verify: Response includes official Florida websites
   - Check: License information with costs and requirements

## 📊 **What to Look For**

### **✅ Successful Response Should Include:**
- **Business Analysis**: Detected business type and requirements
- **License Information**: Specific licenses needed
- **Cost Breakdown**: Application fees, license fees, total costs
- **Timeline**: Processing times and deadlines
- **Source Information**: Official government websites
- **Next Steps**: Action items and application process

### **✅ System Status Indicators:**
- **Chat History**: Number of queries processed
- **API Key Status**: Whether GEMINI_API_KEY is set
- **MCP Components**: Availability of Fetch and Playwright servers
- **Intelligent Semantic Search**: System functionality

## 🔧 **Troubleshooting**

### **If the app doesn't load:**
1. Check if Streamlit is running: `ps aux | grep streamlit`
2. Restart the app: `streamlit run streamlit_app.py --server.port 8502`

### **If you get API errors:**
1. Verify your GEMINI_API_KEY is correct
2. Check the API key format in the sidebar
3. Try the test analysis feature first

### **If responses are generic:**
1. Ensure GEMINI_API_KEY is set
2. Check that MCP components are available
3. Try the test queries in the sidebar

## 🎯 **Testing Checklist**

### **Core Functionality:**
- [ ] Web interface loads correctly
- [ ] Sidebar configuration works
- [ ] Test queries are available
- [ ] Analysis feature works
- [ ] Query processing works

### **Acceptance Criteria:**
- [ ] Query "ice cream franchise in FL" is processed correctly
- [ ] Business type detected as `food_hospitality`
- [ ] Florida-specific licenses are identified
- [ ] Cost estimates are provided ($800-3500)
- [ ] Source information includes official websites
- [ ] Response includes next steps

### **Advanced Features:**
- [ ] Chat history is maintained
- [ ] System status is displayed
- [ ] Error handling works gracefully
- [ ] MCP integration is functional

## 🚀 **Quick Start Commands**

### **Start the Streamlit App:**
```bash
cd BusinessLicenseNavigator
streamlit run streamlit_app.py --server.port 8502
```

### **Access the Web Interface:**
Open: `http://localhost:8502`

### **Test the Ice Cream Scenario:**
1. Select test query in sidebar
2. Click "Test Analysis"
3. Click "Process Query"
4. Verify response meets acceptance criteria

## 📈 **Expected Results**

### **For "I want to open an ice cream franchise in FL for Rita's":**

**Analysis Results:**
- Business Type: `food_hospitality`
- Detected Licenses: 5 licenses (Florida Food Service License, etc.)
- Cost Estimate: $800-3500
- Timeline: 4-8 weeks

**AI Response Should Include:**
- Specific Florida license requirements
- Cost breakdown and fees
- Official Florida government links
- Application process and next steps
- Source attribution and current information

**✅ All acceptance criteria should be met!**

---

**Happy Testing! 🎉**

The Streamlit interface provides a user-friendly way to test all the acceptance criteria for the Business License Navigator application. 