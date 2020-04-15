import functools
import time

import streamlit as st

import streamlit.ReportThread as ReportThread
from streamlit.server.Server import Server

COLOR = "black"
BACKGROUND_COLOR = "#fff"


def select_block_container_style():
    """Add selection section for setting setting the max-width and padding
    of the main block container"""
    st.sidebar.header("Block Container Style")
    max_width_100_percent = st.sidebar.checkbox("Max-width: 100%?", False)
    if not max_width_100_percent:
        max_width = st.sidebar.slider("Select max-width in px", 100, 2000, 1200, 100)
    else:
        max_width = 1200
    padding_top = st.sidebar.number_input("Select padding top in rem", 0, 200, 5, 1)
    padding_right = st.sidebar.number_input("Select padding right in rem", 0, 200, 1, 1)
    padding_left = st.sidebar.number_input("Select padding left in rem", 0, 200, 1, 1)
    padding_bottom = st.sidebar.number_input("Select padding bottom in rem", 0, 200, 10, 1)

    _set_block_container_style(
        max_width, max_width_100_percent, padding_top, padding_right, padding_left, padding_bottom,
    )


def _set_block_container_style(
    max_width: int = 1200,
    max_width_100_percent: bool = False,
    padding_top: int = 5,
    padding_right: int = 1,
    padding_left: int = 1,
    padding_bottom: int = 10,
):
    if max_width_100_percent:
        max_width_str = f"max-width: 100%;"
    else:
        max_width_str = f"max-width: {max_width}px;"
    st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        {max_width_str}
        padding-top: {padding_top}rem;
        padding-right: {padding_right}rem;
        padding-left: {padding_left}rem;
        padding-bottom: {padding_bottom}rem;
    }}
    .reportview-container .main {{
        color: {COLOR};
        background-color: {BACKGROUND_COLOR};
    }}
</style>
""",
        unsafe_allow_html=True,
    )


def get_session_id():
    # Hack to get the session object from Streamlit.

    ctx = ReportThread.get_report_ctx()

    session = None
    session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        s = session_info.session
        if (
            (hasattr(s, "_main_dg") and s._main_dg == ctx.main_dg)
            # Streamlit < 0.54.0
            or
            # Streamlit >= 0.54.0
            (not hasattr(s, "_main_dg") and s.enqueue == ctx.enqueue)
        ):
            session = session_info.session

    if session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object" "Are you doing something fancy with threads?"
        )

    return id(session)


def fancy_cache(func=None, ttl=None, unique_to_session=False, **cache_kwargs):
    """A fancier cache decorator which allows items to expire after a certain time
    as well as promises the cache values are unique to each session.
    Parameters
    ----------
    func : Callable
        If not None, the function to be cached.
    ttl : Optional[int]
        If not None, specifies the maximum number of seconds that this item will
        remain in the cache.
    unique_to_session : boolean
        If so, then hash values are unique to that session. Otherwise, use the default
        behavior which is to make the cache global across sessions.
    **cache_kwargs
        You can pass any other arguments which you might to @st.cache
    """
    # Support passing the params via function decorator, e.g.
    # @fancy_cache(ttl=10)
    if func is None:
        return lambda f: fancy_cache(func=f, ttl=ttl, unique_to_session=unique_to_session, **cache_kwargs)

    # This will behave like func by adds two dummy variables.
    dummy_func = st.cache(
        func=lambda ttl_token, session_token, *func_args, **func_kwargs: func(*func_args, **func_kwargs), **cache_kwargs
    )

    # This will behave like func but with fancy caching.
    @functools.wraps(func)
    def fancy_cached_func(*func_args, **func_kwargs):
        # Create a token which changes every ttl seconds.
        ttl_token = None
        if ttl is not None:
            ttl_token = int(time.time() / ttl)

        # Create a token which is unique to each session.
        session_token = None
        if unique_to_session:
            session_token = get_session_id()

        # Call the dummy func
        return dummy_func(ttl_token, session_token, *func_args, **func_kwargs)

    return fancy_cached_func


class SessionState(object):
    def __init__(self, **kwargs):
        """A new SessionState object.

        Parameters
        ----------
        **kwargs : any
            Default values for the session state.

        Example
        -------
        >>> session_state = SessionState(user_name='', favorite_color='black')
        >>> session_state.user_name = 'Mary'
        ''
        >>> session_state.favorite_color
        'black'

        """
        for key, val in kwargs.items():
            setattr(self, key, val)

    def get(**kwargs):
        """Gets a SessionState object for the current session.

        Creates a new object if necessary.

        Parameters
        ----------
        **kwargs : any
            Default values you want to add to the session state, if we're creating a
            new one.

        Example
        -------
        >>> session_state = get(user_name='', favorite_color='black')
        >>> session_state.user_name
        ''
        >>> session_state.user_name = 'Mary'
        >>> session_state.favorite_color
        'black'

        Since you set user_name above, next time your script runs this will be the
        result:
        >>> session_state = get(user_name='', favorite_color='black')
        >>> session_state.user_name
        'Mary'

        """
        # Hack to get the session object from Streamlit.

        ctx = ReportThread.get_report_ctx()

        this_session = None

        current_server = Server.get_current()
        if hasattr(current_server, "_session_infos"):
            # Streamlit < 0.56
            session_infos = Server.get_current()._session_infos.values()
        else:
            session_infos = Server.get_current()._session_info_by_id.values()

        for session_info in session_infos:
            s = session_info.session
            if (
                # Streamlit < 0.54.0
                (hasattr(s, "_main_dg") and s._main_dg == ctx.main_dg)
                or
                # Streamlit >= 0.54.0
                (not hasattr(s, "_main_dg") and s.enqueue == ctx.enqueue)
            ):
                this_session = s

        if this_session is None:
            raise RuntimeError(
                "Oh noes. Couldn't get your Streamlit Session object" "Are you doing something fancy with threads?"
            )

        # Got the session object! Now let's attach some state into it.

        if not hasattr(this_session, "_custom_session_state"):
            this_session._custom_session_state = SessionState(**kwargs)

        return this_session._custom_session_state
