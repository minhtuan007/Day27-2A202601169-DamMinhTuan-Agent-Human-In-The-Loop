# 1. Thuật ngữ cần biết

Bản đồ Lab

### Đọc trước khi bắt đầu

120 phútTrung cấp

Xây dựng một LangGraph workflow cho bài toán đánh giá churn risk của khách hàng, kết hợp agent reasoning, confidence routing, hard policy rules, human approval bằng Streamlit và audit logging.

#### Bài này đang nói về điều gì?

Thiết kế persistent state cho LangGraph bằng TypedDict

Thiết kế audit schema bằng Pydantic

Xây dựng agent reasoning node với action, confidence score và reasoning

Kết hợp confidence routing với hard policy rules

Dùng interrupt_before và MemorySaver để triển khai Human-in-the-Loop

Xây dựng giao diện Approve, Reject và Edit bằng Streamlit

Ghi lại quyết định của agent và con người vào audit trail

1. Customer data -> Agent reasoning -> Proposed action + confidence score
2. Hard rules và confidence routing -> Auto-execute hoặc chuyển sang human review
3. LangGraph interrupt -> Streamlit approval interface -> Approve, Reject hoặc Edit
4. Resume graph -> Execute/abort action -> Audit log

#### Buổi Lab diễn ra như thế nào?

1. 20 phútCá nhân
    
    ##### State và Audit Schema
    
    Định nghĩa GraphState và AuditEntry để lưu trạng thái workflow và dữ liệu audit.
    
2. 25 phútCá nhân
    
    ##### Agent Reasoning và Routing
    
    Xây dựng node đánh giá khách hàng, confidence score và conditional routing kết hợp hard rules.
    
3. 25 phútCá nhân
    
    ##### Compile Graph với Interrupts
    
    Sử dụng MemorySaver và interrupt_before để dừng workflow trước hành động high-risk.
    
4. 30 phútCá nhân
    
    ##### Streamlit Human Approval
    
    Xây dựng giao diện cho human operator xem, Approve, Reject hoặc Edit pending action.
    
5. 20 phútCá nhân
    
    ##### Audit Log và kiểm tra
    
    Ghi lại quyết định vào audit trail và kiểm tra toàn bộ luồng Human-in-the-Loop.
    

#### Kết thúc bài, bạn có gì?

- Xây dựng được LangGraph workflow có persistent state
- Agent đưa ra proposed action, reasoning và confidence score
- Workflow áp dụng hard policy rules và confidence routing
- High-risk action bị dừng để chờ human approval
- Human operator có thể Approve, Reject hoặc Edit action qua Streamlit
- Mọi quyết định được lưu vào audit trail

Chưa cần lo

Không cần xây một hệ thống ngân hàng hoàn chỉnh. Trọng tâm của Lab là hiểu đúng luồng Human-in-the-Loop: agent đề xuất, policy quyết định route, graph tạm dừng khi cần và con người đưa ra quyết định cuối cùng trước hành động rủi ro cao.

| Thuật ngữ gốc              | Bản chất khái niệm                                                                                                                      | Minh hoạ trực quan                                                                                      |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `Human-in-the-Loop (HITL)` | Kiến trúc trong đó AI không được tự thực hiện mọi hành động mà phải chuyển một số quyết định cho con người kiểm tra trước khi tiếp tục. | Agent đề xuất tăng hạn mức tín dụng nhưng workflow dừng lại để nhân viên ngân hàng Approve hoặc Reject. |
| `LangGraph`                | Framework xây workflow dạng graph cho agent, cho phép quản lý state, routing, checkpoint và tạm dừng/resume execution.                  | Customer data đi qua các node đánh giá -> routing -> human review -> execution.                         |
| `GraphState`               | Trạng thái dùng chung được truyền qua các node trong graph và lưu thông tin cần thiết của workflow.                                     | Lưu `customer_id`, `proposed_action`, `confidence_score`, `reasoning`, `human_decision`.                |
| `TypedDict`                | Cách khai báo cấu trúc dictionary có kiểu dữ liệu rõ ràng trong Python.                                                                 | Dùng để mô tả chính xác các field tồn tại trong `GraphState`.                                           |
| `AuditEntry`               | Schema đại diện cho một bản ghi audit để biết agent đã đề xuất gì, confidence bao nhiêu và con người quyết định thế nào.                | Một record có `timestamp`, `agent_id`, `action`, `confidence`, `reviewer_id`, `decision`.               |
| `Confidence Score`         | Điểm thể hiện mức độ tự tin của agent đối với quyết định của mình, thường nằm từ 0.0 đến 1.0.                                           | `0.92` có thể auto-execute low-risk action, còn `0.72` phải human review.                               |
| `Confidence Routing`       | Cơ chế dùng confidence score để quyết định workflow đi sang nhánh nào.                                                                  | Confidence >= 0.85 và action low-risk -> auto execute.                                                  |
| `Hard Rule`                | Quy tắc cứng có độ ưu tiên cao hơn confidence của agent.                                                                                | `increase_credit_limit` luôn phải human review dù confidence là 0.99.                                   |
| `Policy Override`          | Trường hợp policy cưỡng chế route, không cho confidence của agent quyết định.                                                           | Action tăng hạn mức luôn đi tới high-risk path.                                                         |
| `MemorySaver`              | Checkpointer của LangGraph dùng để lưu state để workflow có thể tạm dừng và tiếp tục sau đó.                                            | Graph dừng trước high-risk action nhưng customer data không bị mất khi chờ người review.                |
| `interrupt_before`         | Cấu hình yêu cầu LangGraph dừng trước khi chạy một node cụ thể.                                                                         | `interrupt_before=["execute_high_risk_action"]` dừng graph trước khi hành động nguy hiểm được thực thi. |
| `Pending State`            | Trạng thái workflow đang tạm dừng để chờ quyết định từ bên ngoài.                                                                       | Streamlit lấy pending state và hiển thị proposed action cho reviewer.                                   |
| `Audit Trail`              | Nhật ký bất biến hoặc có thể kiểm toán về các quyết định và hành động đã diễn ra trong workflow.                                        | Ghi agent đề xuất gì, confidence bao nhiêu, ai review và quyết định cuối cùng là gì.                    |
| `Approve`                  | Human reviewer đồng ý với proposed action và cho workflow tiếp tục.                                                                     | Cho phép thực hiện `increase_credit_limit`                                                              |
|                            |                                                                                                                                         |                                                                                                         |
| `Reject`                   | Human reviewer từ chối proposed action và yêu cầu workflow hủy hành động.                                                               | Không thực hiện thay đổi hạn mức tín dụng.                                                              |
| `Edit`                     | Human reviewer sửa proposed action trước khi workflow tiếp tục.                                                                         | Agent đề xuất tăng 50 triệu, reviewer sửa thành tăng 20 triệu rồi approve.                              |

# 2. Mục tiêu & đầu ra

Bạn hoàn thành khi xây dựng được một LangGraph workflow đánh giá rủi ro khách hàng rời bỏ (`churn risk`) và xử lý hành động bằng cơ chế Human-in-the-Loop.

Workflow cần thực hiện được toàn bộ luồng:

```text
Customer Data
      |
      v
Agent Reasoning
      |
      | proposed_action
      | confidence_score
      | reasoning
      v
Confidence Routing + Hard Rules
      |
      +-----------------------------+
      |                             |
      | Low-risk                    | High-risk / cần review
      v                             v
Auto Execute                  Interrupt Graph
                                    |
                                    v
                             Streamlit Review
                              /      |      \
                         Approve   Reject    Edit
                            |        |        |
                            +--------+--------+
                                     |
                                     v
                                Resume Graph
                                     |
                                     v
                                 Audit Log
```

Copy

Đầu ra cần có:

- Một `GraphState` lưu:
    
    - `customer_id`
    - `proposed_action`
    - `confidence_score`
    - `reasoning`
    - `human_decision`
- Một Pydantic `AuditEntry` có:
    
    - `timestamp`
    - `agent_id`
    - `action`
    - `confidence`
    - `reviewer_id`
    - `decision`
- Một node:
    

```python
evaluate_customer(state)
```

Copy

đánh giá khách hàng và trả về:

- `proposed_action`
    
- `confidence_score`
    
- `reasoning`
    
- Một conditional edge function:
    

```python
route_action(state)
```

Copy

thực hiện:

- Policy Override.
    
- Auto-Execute.
    
- Escalate/Suggest.
    
- LangGraph được compile với:
    
    - `MemorySaver()`
    - `interrupt_before=["execute_high_risk_action"]`
- Một Streamlit approval interface cho phép:
    
    - Approve.
    - Reject.
    - Edit.
- Một audit trail ghi lại quyết định của agent và human reviewer.
# 3. Chuẩn bị

Liệt kê công cụ, dữ liệu và điều kiện tối thiểu.

### Python

Yêu cầu:

```text
Python 3.10+
```

Copy

### Thư viện

Cài các thư viện:

```bash
pip install langgraph langchain streamlit pydantic
```

Copy

Các thư viện chính:

```text
langgraph
langchain
streamlit
pydantic
```

Copy

### Cấu trúc project gợi ý

```text
day27-hitl/
├── app.py
├── graph.py
├── models.py
├── audit_log.json
└── requirements.txt
```

Copy

Trong đó:

```text
graph.py
```

Copy

chứa:

- GraphState.
- Agent nodes.
- Routing.
- Graph compilation.

```text
models.py
```

Copy

chứa:

- AuditEntry.

```text
app.py
```

Copy

chứa:

- Streamlit UI.
- Human approval logic.
- Resume graph logic.

```text
audit_log.json
```

Copy

chứa:

- Audit trail.
# 4. Thực hành

**Bước 1 - Định nghĩa State và Audit Schema**

Graph cần một persistent state để giữ proposed action của agent trong khi chờ human approval.

Tạo một `GraphState` sử dụng `TypedDict`.

State bao gồm các key:

```text
customer_id
proposed_action
confidence_score
reasoning
human_decision
```

Copy

Ví dụ:

```python
from typing import TypedDict

class GraphState(TypedDict):
    customer_id: str
    proposed_action: str
    confidence_score: float
    reasoning: str
    human_decision: str | None
```

Copy

GraphState cần tồn tại xuyên suốt workflow.

Ví dụ:

```text
Agent đề xuất action
        |
        v
GraphState
        |
        | graph tạm dừng
        v
Human Review
        |
        | cập nhật decision
        v
GraphState
```

Copy

Tiếp theo, định nghĩa một Pydantic `BaseModel` có tên:

```text
AuditEntry
```

Copy

bao gồm:

```text
timestamp
agent_id
action
confidence
reviewer_id
decision
```

Copy

Ví dụ:

```python
from pydantic import BaseModel

class AuditEntry(BaseModel):
    timestamp: str
    agent_id: str
    action: str
    confidence: float
    reviewer_id: str
    decision: str
```

Copy

Mục tiêu của audit schema là lưu lại đầy đủ:

```text
Agent nào đưa ra quyết định?
Hành động được đề xuất là gì?
Confidence bao nhiêu?
Ai review?
Human quyết định gì?
Thời điểm nào?
```

Copy

---

**Bước 2 - Implement Agent Reasoning Node**

Giả lập một agent đánh giá:

```text
Total Operating Income (TOI)
```

Copy

và:

```text
churn probability
```

Copy

của khách hàng.

Tạo một node function:

```python
evaluate_customer(state)
```

Copy

Ví dụ:

```python
def evaluate_customer(state: GraphState):
    ...
```

Copy

Có thể:

- Hardcode một mock LLM output.
- Hoặc sử dụng một prompt cơ bản để generate mock output.

Agent cần đề xuất một action.

Action có thể là:

```text
send_email
```

Copy

cho trường hợp:

```text
low-risk
```

Copy

hoặc:

```text
increase_credit_limit
```

Copy

cho trường hợp:

```text
high-risk
```

Copy

Node phải output một:

```text
confidence_score
```

Copy

trong khoảng:

```text
0.0 -> 1.0
```

Copy

Ví dụ output:

```python
{
    "proposed_action": "send_email",
    "confidence_score": 0.92,
    "reasoning": "Customer has moderate churn probability and no high-risk financial action is required."
}
```

Copy

Hoặc:

```python
{
    "proposed_action": "increase_credit_limit",
    "confidence_score": 0.96,
    "reasoning": "Customer has high churn probability and increasing the credit limit may improve retention."
}
```

Copy

Lưu ý:

```text
confidence_score cao KHÔNG có nghĩa là agent được phép bypass policy.
```

Copy

Hard policy rule ở bước tiếp theo có quyền override confidence.

---

**Bước 3 - Implement Confidence Routing và Hard Rules**

Tạo một conditional edge function:

```python
route_action(state)
```

Copy

để xác định bước tiếp theo dựa trên output của agent.

Ví dụ:

```python
def route_action(state: GraphState):
    ...
```

Copy

Routing phải thực hiện ba rule.

**Rule 1 - Policy Override**

Nếu action là:

```text
increase_credit_limit
```

Copy

thì route thẳng đến:

```text
execute_high_risk_action
```

Copy

bất kể:

```text
confidence_score
```

Copy

là bao nhiêu.

Ví dụ:

```text
action = increase_credit_limit
confidence = 0.99
```

Copy

vẫn phải:

```text
Human Review
```

Copy

Không được auto-execute.

Luồng:

```text
increase_credit_limit
        |
        | hard policy rule
        v
execute_high_risk_action
        |
        | interrupt_before
        v
Human Review
```
**Rule 2 - Auto-Execute**

Nếu:

```text
confidence_score >= 0.85
```

Copy

và action là:

```text
low-risk
```

Copy

thì route đến:

```text
execute_low_risk_action
```

Copy

Ví dụ:

```text
action = send_email
confidence_score = 0.91
```

Copy

thì:

```text
Auto Execute
```

Copy

**Rule 3 - Escalate/Suggest**

Nếu:

```text
confidence_score < 0.85
```

Copy

thì route đến:

```text
execute_high_risk_action
```

Copy

để ép buộc human review.

Ví dụ:

```text
action = send_email
confidence_score = 0.82
```

Copy

mặc dù action là low-risk nhưng confidence thấp hơn threshold nên:

```text
Human Review
```

Copy

Tóm tắt routing:

```text
                     proposed_action
                            |
                            v
                +-------------------------+
                | increase_credit_limit ? |
                +-------------------------+
                     | YES          | NO
                     v              v
                 High Risk     confidence >= 0.85 ?
                                      |
                               +------+------+
                               |             |
                              YES            NO
                               |             |
                               v             v
                          Low Risk       High Risk
```

Copy

---

**Bước 4 - Compile Graph với Interrupts**
Đây là phần lõi của HITL architecture.

Bạn phải pause graph trước khi bất kỳ destructive action hoặc high-risk action nào diễn ra.

Khởi tạo:

```text
MemorySaver()
```

Copy

checkpointer.

Import:

```python
from langgraph.checkpoint.memory import MemorySaver
```

Copy

Khởi tạo:

```python
memory = MemorySaver()
```

Copy

Điều này là bắt buộc.

Nếu không có persistent checkpoint, graph có thể mất customer data trong khi chờ con người review.

Build state graph và kết nối các node.

Các node có thể gồm:

```text
evaluate_customer
execute_low_risk_action
execute_high_risk_action
```

Copy

Sau đó compile graph:

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["execute_high_risk_action"]
)
```

Copy

Điểm quan trọng:

```text
interrupt_before=["execute_high_risk_action"]
```

Copy

có nghĩa là:

```text
Graph KHÔNG chạy execute_high_risk_action ngay.

Graph dừng TRƯỚC node đó.
```

Copy

Luồng:

```text
evaluate_customer
       |
       v
route_action
       |
       v
execute_high_risk_action
       X
       |
       | INTERRUPT BEFORE
       v
Human Review
```

Copy

State phải vẫn tồn tại trong lúc graph đang tạm dừng.

---

**Bước 5 - Xây dựng Streamlit Approval Interface**

Tạo một front-end dashboard nơi human operator review các pending actions.

Tạo:

```text
app.py
```

Copy

Setup một Streamlit app.

Ví dụ chạy:

```bash
streamlit run app.py
```

Copy

Khởi tạo compiled graph trong:
```text
session_state
```

Copy

để graph không bị tạo lại không cần thiết mỗi lần Streamlit rerun.

Sử dụng:

```python
graph.get_state(config)
```

Copy

để lấy pending state hiện tại.

Trích xuất:

```text
proposed_action
confidence_score
reasoning
```

Copy

Render một Action Card trong Streamlit.

Ví dụ thông tin:

```text
Customer ID: CUST001

Proposed Action:
increase_credit_limit

Confidence:
0.91

Reasoning:
Customer has high churn probability...
```

Copy

Thêm ba button:

```text
Approve
Reject
Edit
```

Copy

**Approve**

Human operator đồng ý với action.

Ví dụ:

```text
human_decision = "approve"
```

Copy

**Reject**

Human operator từ chối action.

Ví dụ:

```text
human_decision = "reject"
```

Copy

**Edit**

Human operator chỉnh sửa proposed action trước khi tiếp tục.

Ví dụ:

```text
Agent:
increase_credit_limit = 50,000,000

Human Edit:
increase_credit_limit = 20,000,000
```

Copy

Khi một button được click, trigger:

```python
graph.update_state(
    config,
    {"human_decision": decision}
)
```

Copy

Sau đó invoke graph lại:

```python
graph.invoke(None, config)
```

Copy

để resume execution.

Luồng:

```text
Graph interrupted
       |
       v
Streamlit UI
       |
       +-------- Approve
       |
       +-------- Reject
       |
       +-------- Edit
       |
       v
graph.update_state(...)
       |
       v
graph.invoke(None, config)
       |
       v
Resume Graph
```

Copy

---

**Bước 6 - Ghi Audit Log**

Chỉnh sửa node:

```text
execute_high_risk_action
```

Copy

để kiểm tra:

```text
state["human_decision"]
```

Copy

Nếu decision là:

```text
Approve
```

Copy

thì:

```text
execute action
```

Copy

Ví dụ:

```text
increase_credit_limit
```

Copy

được phép thực hiện.

Nếu decision là:

```text
Reject
```

Copy

thì:

```text
abort action
```

Copy

Không thực hiện proposed action.

Nếu decision là:

```text
Edit
```

Copy

thì thực hiện action sau khi đã được human operator chỉnh sửa.

Trong tất cả các trường hợp, khởi tạo một:

```text
AuditEntry
```

Copy

và append vào một file JSON cục bộ.

Ví dụ:

```json
{
  "timestamp": "2026-08-29T09:00:00",
  "agent_id": "churn-risk-agent",
  "action": "increase_credit_limit",
  "confidence": 0.94,
  "reviewer_id": "operator_01",
  "decision": "approve"
}
```
Ví dụ:

```json
{
  "timestamp": "2026-08-29T09:00:00",
  "agent_id": "churn-risk-agent",
  "action": "increase_credit_limit",
  "confidence": 0.94,
  "reviewer_id": "operator_01",
  "decision": "approve"
}
```

Copy

File:

```text
audit_log.json
```

Copy

có thể có dạng:

```json
[
  {
    "timestamp": "2026-08-29T09:00:00",
    "agent_id": "churn-risk-agent",
    "action": "increase_credit_limit",
    "confidence": 0.94,
    "reviewer_id": "operator_01",
    "decision": "approve"
  }
]
```

Copy

Mục tiêu:

```text
Mọi quyết định quan trọng phải truy vết được.
```

Copy

Trong production, có thể ghi log vào:

```text
PostgreSQL append-only database
```

Copy

để tăng độ tin cậy và khả năng kiểm toán.

---

**Reflection Questions**

**Câu 1**

Ở Bước 4, chúng ta đã dùng:

```python
interrupt_before=["execute_high_risk_action"]
```

Copy

Nếu mục tiêu của bạn là để con người rewrite một customer retention email vừa được generate trước khi nó di chuyển đến một routing node, bạn sẽ dùng:

```text
interrupt_before
```

Copy

hay:

```text
interrupt_after
```

Copy

Tại sao?

---

**Câu 2**

Giả sử Streamlit UI của bạn hiện đang ép human phải review:

```text
500 actions send_email mỗi ngày
```

Copy

vì confidence của agent bị kẹt ở:

```text
0.82
```
ngay dưới threshold:

```text
0.85
```

Copy

Hãy thay đổi cụ thể về UI/UX hoặc architecture nào bạn có thể thực hiện để ngăn chặn:

```text
Alert Fatigue
```

Copy

(Hội chứng mệt mỏi vì cảnh báo)?

---

**Câu 3**

Bạn nhận thấy agent thường xuyên tự báo confidence là:

```text
0.95
```

Copy

khi đề xuất:

```text
increase_credit_limit
```

Copy

nhưng nó lại thường xuyên sai về thu nhập thực tế của khách hàng.

Tại sao việc chỉ phụ thuộc vào sự tự đánh giá confidence của LLM lại nguy hiểm?

Và làm thế nào bạn có thể calibrate điểm số này trước bước routing?
# 5. Kiểm tra kết quả

Nêu cách tự kiểm tra và lỗi thường gặp.

### Kiểm tra State

Đảm bảo `GraphState` có:

```text
customer_id
proposed_action
confidence_score
reasoning
human_decision
```

Copy

Kiểm tra:

```text
[ ] State tồn tại xuyên suốt graph
[ ] State không mất khi graph bị interrupt
[ ] human_decision có thể được cập nhật từ Streamlit
```

Copy

### Kiểm tra Agent Reasoning

Chạy một customer input.

Đảm bảo agent output:

```text
[ ] proposed_action
[ ] confidence_score
[ ] reasoning
```

Copy

và:

```text
0.0 <= confidence_score <= 1.0
```

Copy

### Kiểm tra Hard Rule

Test:

```text
proposed_action = increase_credit_limit
confidence_score = 0.99
```

Copy

Kết quả bắt buộc:

```text
Human Review
```

Copy

Không được:

```text
Auto Execute
```

Copy

### Kiểm tra Auto-Execute

Test:

```text
proposed_action = send_email
confidence_score = 0.90
```

Copy

Kết quả:

```text
execute_low_risk_action
```

Copy

### Kiểm tra Escalation

Test:

```text
proposed_action = send_email
confidence_score = 0.82
```

Copy

Kết quả:

```text
Human Review
```

Copy

### Kiểm tra Interrupt

Đảm bảo graph compile với:

```python
graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["execute_high_risk_action"]
)
```

Copy

Khi route tới high-risk action:

```text
[ ] execute_high_risk_action chưa được chạy
[ ] graph ở pending state
[ ] state vẫn còn dữ liệu customer
```

Copy

### Kiểm tra Streamlit

Streamlit UI phải hiển thị:

```text
[ ] proposed_action
[ ] confidence_score
[ ] reasoning
[ ] Approve
[ ] Reject
[ ] Edit
```

Copy

Test Approve:
```text
Approve
   |
   v
update_state
   |
   v
resume graph
   |
   v
execute action
```

Copy

Test Reject:

```text
Reject
   |
   v
update_state
   |
   v
resume graph
   |
   v
abort action
```

Copy

### Kiểm tra Audit Log

Sau mỗi human decision, `audit_log.json` phải có entry mới.

Entry phải chứa:

```text
timestamp
agent_id
action
confidence
reviewer_id
decision
```

Copy

Đảm bảo:

```text
[ ] Approve được log
[ ] Reject được log
[ ] Edit được log
[ ] Không overwrite audit history cũ
```

Copy

### Lỗi thường gặp

**Graph mất state sau khi interrupt**

Kiểm tra có dùng:

```python
MemorySaver()
```

Copy

và truyền vào:

```python
checkpointer=memory
```

Copy

hay chưa.

**High-risk action chạy trước khi human review**

Kiểm tra:

```python
interrupt_before=["execute_high_risk_action"]
```

Copy

không phải interrupt sau khi action đã được thực hiện.

**Hard rule bị confidence override**

Sai:

```text
confidence = 0.99
-> auto execute increase_credit_limit
```

Copy

Đúng:

```text
increase_credit_limit
-> luôn human review
```

Copy

Hard policy phải được kiểm tra trước confidence threshold.

**Streamlit bấm button nhưng graph không tiếp tục**

Kiểm tra:

```python
graph.update_state(config, ...)
```

Copy

và sau đó:

```python
graph.invoke(None, config)
```

Copy

để resume graph.

**Pending state không lấy được**

Kiểm tra:

```python
graph.get_state(config)
```

Copy

và `config` phải dùng cùng `thread_id` với lần invoke trước đó.

**Audit log bị ghi đè**

Không ghi một object mới đè lên toàn bộ lịch sử.

Cần:

1. Đọc audit entries hiện có.
2. Append `AuditEntry` mới.
3. Ghi lại danh sách.

Trong production nên dùng append-only database.
# 6. Nộp bài

Hình thức: cá nhân.

Artefact cần nộp:

- Link repository GitHub cá nhân chứa bài làm Lab 27.

Repository cần có tối thiểu:

```text
GraphState
AuditEntry
evaluate_customer
route_action
execute_low_risk_action
execute_high_risk_action
MemorySaver
interrupt_before
Streamlit approval interface
audit log
```

Copy

README cần mô tả:

- Cách cài dependency.
- Cách chạy LangGraph workflow.
- Cách chạy Streamlit UI.
- Confidence threshold đang sử dụng.
- Hard policy rule.
- Cách Approve, Reject và Edit.
- Audit log được lưu ở đâu.

Ví dụ chạy:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Copy

Repository không nên chứa:

```text
API key
Access token
Password
Private key
.env chứa credential thật
```