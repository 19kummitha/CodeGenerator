import streamlit as st
from openai_sql import generate_sql_from_user_input
from openai_code import generate_code_from_user_input, explain_code
from database import SessionLocal, OutputHistory
from datetime import datetime

st.set_page_config(page_title="AI Code & SQL Generator", page_icon="💡", layout="wide")
st.title("💡 AI Code & SQL Generator")

tab_generate, tab_history = st.tabs(["🚀 Generate"])

# ========== GENERATE TAB ==========
with tab_generate:
    task_type = st.selectbox("What do you want to generate?", ["Database (SQL)", "Programming (Code)"])

    schema = ""
    if task_type == "Database (SQL)":
        schema = st.text_area("🗃️ Database Schema (DDL)", height=200, placeholder="CREATE TABLE users (...);")

    language = None
    if task_type == "Programming (Code)":
        language = st.selectbox("Choose programming language", ["Python", "Java", "C", "C++", "C#"])

    question = st.text_area("❓ Your Question", height=100, placeholder="E.g., Write a program to reverse a string")

    if st.button("🚀 Generate"):
        if not question.strip() or (task_type == "Database (SQL)" and not schema.strip()):
            st.error("Please complete all required fields.")
        else:
            with st.spinner("Generating output..."):
                try:
                    code = ""
                    explanation = None

                    if task_type == "Database (SQL)":
                        code = generate_sql_from_user_input(schema, question)
                    else:
                        code = generate_code_from_user_input(language, question)
                        explanation = explain_code(language, code)

                    st.success("✅ Output Generated")
                    st.markdown("### 📄 Generated Code")
                    st.code(code, language=language.lower() if language else "sql")
                    st.download_button("📥 Download Code", code, file_name=f"generated.{language.lower() if language else 'sql'}")

                    if explanation:
                        st.markdown("### 🧠 Code Explanation")
                        st.write(explanation)

                    # Save to database
                    db = SessionLocal()
                    db.add(OutputHistory(
                        mode="SQL" if task_type == "Database (SQL)" else "Code",
                        language=language if task_type == "Programming (Code)" else None,
                        question=question,
                        schema=schema if task_type == "Database (SQL)" else None,
                        response=code,
                        explanation=explanation,
                        created_at=datetime.utcnow()
                    ))
                    db.commit()
                    db.close()

                except Exception as e:
                    st.error(f"❌ Error: {e}")

# # ========== HISTORY TAB ==========
# with tab_history:
#     st.subheader("🕘 Previous Generations")

#     db = SessionLocal()
#     history = db.query(OutputHistory).order_by(OutputHistory.created_at.desc()).all()
#     db.close()

#     if not history:
#         st.info("No history found.")
#     else:
#         for record in history:
#             with st.expander(f"{record.mode} | {record.language or 'SQL'} | {record.created_at.strftime('%Y-%m-%d %H:%M:%S')}"):
#                 st.markdown(f"**❓ Question:** {record.question}")
#                 if record.schema:
#                     with st.expander("📦 Schema"):
#                         st.code(record.schema, language="sql")
#                 st.markdown("**🧾 Response:**")
#                 st.code(record.response, language=(record.language.lower() if record.language else "sql"))
#                 if record.explanation:
#                     st.markdown("**🧠 Explanation:**")
#                     st.write(record.explanation)
