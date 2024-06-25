import streamlit as st
import hmac

if 'test_ready' not in st.session_state:
    st.session_state['test_ready'] = False



def check_password():
    """Returns `True` if the user had a correct password."""
    st.session_state["password_correct"] = True
    return True

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.subheader("Please login here:")
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["passwords"] and \
                hmac.compare_digest(st.session_state["password"], st.secrets.passwords[st.session_state["username"]],):
            st.session_state["password_correct"] = True
            st.session_state["username_value"] = st.session_state["username"]
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


def main():
    st.set_page_config(page_title="Welcome page", page_icon="👋", layout='wide')

    if not check_password():
        st.stop()

    st.header(f"Welcome to LLM testbench *Local Guy*")
    st.sidebar.success("Start from instructions and then proceed according to the chosen test method.")

    st.markdown("""
        ### Short introduction:
        This page has been created for testing LLM's (OpenAI's GPT-4) capabilities in finding conflicts from construction 
        industry documents. The results will be reported in a thesis _Generative AI for identifying conflicts in 
        construction industry documents_ written by _Tapio Pulkkinen_. You can find more 
        information of this thesis and about the work from the 'About this thesis work' -page. 
        
        #### How you should use this:
        Note that it is important to fulfill all the asked variables to be able to use the tests properly. **NOTE that all variables will reset if you refresh the page!**
        
        1. If you need instructions, head to the 'Instructions for the testbench'-page from the left sidebar.
        2. Go to the 'Database manager'-page to set up database connection. You can also use in-memory storage but it is not recommended.
        3. Go to the 'Doc and text handling'-page and load the file or files you wish to use in conflict search.
        5. Go to the 'LLM setup'-page and fulfill the large language model's access credentials and parameters. OpenAI's endpoint is recommended.
        6. Go to the 'test #1 - LLM conversation'-page and choose a proper prompt for your use case. You can also write your own prompt is you wish. Then test set-up and log the initial results there.
        7. Do the other tests that can be found from the left side bar.
        """)

    if st.button("Log out"):
        del st.session_state["password_correct"]
        del st.session_state['username_value']
        st.rerun()



if __name__ == "__main__":
    main()
