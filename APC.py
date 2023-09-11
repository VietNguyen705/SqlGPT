import openai
import gradio as gr
import mysql.connector
import sqlparse  # new import

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="inventorydb"
)


openai.api_key = "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"

messages=[]
def chatbot(input):
    if input:
        messages.append({"role": "user", "content": input})
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
              {
                "role": "system",
                "content": "You will be working with a mysql database called inventorydb (already set as default), the table you will always work with is called computerinventory, which stores all the computers, the fields in this table are purchase_year(datatype: year), inventory_id, machine_model, , first_name, last_name,location(location examples like '74' or '74-115' because it represents the building number), status, only provide the query as if you are executing the query itself"
              },
              {
                "role": "user",
                "content": str(input)
              }
            ],
            temperature=0,
            max_tokens=1024
          )
      
        reply = chat.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        sql_query = str(reply).strip()
        cursor = cnx.cursor()
        try:
            sqlparse.parse(sql_query)  # This will raise an exception if sql_query is not a valid SQL statement.
            cursor.execute(sql_query)
            cursor.fetchall()  # fetch all rows and discard them
            cnx.commit()
            cursor.close()
        except Exception as e:
            cursor.close()  # only close cursor if an exception occurred
            return str(e)  # Return the error message if the SQL query is not valid.
        cursor.close()  # close cursor if no exception occurred
        return reply

inputs = gr.inputs.Textbox(lines=7, label="Chat with AI")
outputs = gr.outputs.Textbox(label="Reply")

gr.Interface(fn=chatbot, inputs=inputs, outputs=outputs, title="AI Chatbot",
             description="Ask anything you want",
             theme="compact").launch(share=False)