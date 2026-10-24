import requests
import streamlit as st

API = "http://127.0.0.1:8000"

st.title("Meta Analytics")

if "token" not in st.session_state:
    st.session_state.token = None


def post_json(path, payload):
    try:
        response = requests.post(f"{API}{path}", json=payload, timeout=5)
    except requests.RequestException:
        st.error("Cannot reach the API. Start uvicorn, then try again.")
        return None

    if response.status_code >= 400:
        st.error(response.json().get("detail", "Request failed"))
        return None
    return response.json()


def signed_in_email(token):
    try:
        response = requests.get(
            f"{API}/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
    except requests.RequestException:
        st.error("Cannot reach the API. Start uvicorn, then refresh this page.")
        return None

    if response.status_code == 401:
        st.session_state.token = None
        return None
    if response.status_code >= 400:
        st.error("Could not load your account.")
        return None
    return response.json()["email"]


if st.session_state.token is None:
    st.write("Create an account or sign in. The API stores the account, and this page keeps the token.")
    sign_in_tab, create_account_tab = st.tabs(["Sign in", "Create account"])

    with sign_in_tab:
        with st.form("sign_in"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in")
        if submitted:
            result = post_json("/signin", {"email": email, "password": password})
            if result is not None:
                st.session_state.token = result["token"]
                st.rerun()

    with create_account_tab:
        with st.form("create_account"):
            email = st.text_input("Email", key="new_email")
            password = st.text_input("Password", type="password", key="new_password")
            submitted = st.form_submit_button("Create account")
        if submitted:
            result = post_json("/signup", {"email": email, "password": password})
            if result is not None:
                st.session_state.token = result["token"]
                st.rerun()
else:
    email = signed_in_email(st.session_state.token)
    if email is not None:
        st.write(f"Signed in as **{email}**.")
        if st.button("Sign out"):
            try:
                requests.post(
                    f"{API}/signout",
                    headers={"Authorization": f"Bearer {st.session_state.token}"},
                    timeout=5,
                )
            except requests.RequestException:
                st.error("Cannot reach the API. Start uvicorn, then try again.")
            else:
                st.session_state.token = None
                st.rerun()

        st.divider()
        st.write("This sample preview stays behind sign-in.")
        report_name = st.text_input("Report name", "October report")
        days = st.slider("Days to include", min_value=1, max_value=30, value=7)
        st.write(f"**{report_name}** would cover the last **{days}** days.")
        if st.button("Build preview"):
            st.success(f"Preview ready for {report_name}.")
            spend = [120, 90, 140, 110, 160, 130, 150][:days]
            st.metric("Sample spend", f"${sum(spend)}")
            st.line_chart(spend)
        else:
            st.info("Press the button to build a preview.")
