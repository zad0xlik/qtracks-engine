--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.17
-- Dumped by pg_dump version 9.5.17

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_tokens (
    id integer NOT NULL,
    user_id integer,
    account_number character varying(15),
    access_token character varying,
    refresh_token character varying,
    last_refresh bigint
);


ALTER TABLE public.auth_tokens OWNER TO postgres;

--
-- Name: auth_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_tokens_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_tokens_id_seq OWNER TO postgres;

--
-- Name: auth_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_tokens_id_seq OWNED BY public.auth_tokens.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(20),
    password character varying(20)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens ALTER COLUMN id SET DEFAULT nextval('public.auth_tokens_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: auth_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_tokens (id, user_id, account_number, access_token, refresh_token, last_refresh) FROM stdin;
2	2	789494272	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212FD3x19z9sWBHDJACbC00B75E	1561577332815
1	1	885084780	QETLOxejwCotEAfg13Fjk1r1mXtZ1Sk0sdyL6mp4tSDiCaRvkqB0ddQyI9TqwQgROHBKDTVzzvO60z5yhptRLSGqqLTrSvnJ/4v+qhSx6pNwa/9xoHlZX/Vtti6hfW0Q5GFNj4d9sfn02gbDOM8LyQ+3IGYP5Ln/IJkdzou8qmQyPxcFIqWqtewoBNgM//FwG2O3qoYmIx20741xYUq6zg2A7CK584zSNZFM7abrrNrqkLgl3l5VZ5fVnlMudknmUENWq0K4VZSP8JZqAtbn/gg5FUsQzP4Y9eOXptSs83DI2N5lsCWH+byGtRuXb5uUjYzrocI0ut1BJ2TU6MLa8U1U0RhKDrwBOnPu9cOK/BAv8A5Bh39jW05bdTXb6Hu7sjS/nZMMUs56FIx5bQ23/JluoiSa7E3qlGL6n8mGpxf2bQG85NsGjsCGtfZLQPfYU3AXojMUBGMBnUrFqruI7xUF6Gw+mDx1DKuSro4exMqX7e/11aTXs/QcIsKSwl1G40ycj3ScPjtuadOEGDDxfB9U+jmzuDKraVqf4l7C8MwqwPdTsvnfFhm5mba+lxdulws9JxI2GYUbaqFb1100MQuG4LYrgoVi/JHHvlJLhj8Buu5eX999ylep3whL87FyAdPr4S4Wnhd5Kdte2SfQfNe4GqLVPiJPXTdTLAxl5WqgHs5L+XpL/ptFUqtcxikQ24cnqxgq2uVJF6EGYw29JSdPezpc8kysOVBwQzq33yaivAGwDWsRafWDnhxnPny0HdhPeN3O+12xZg8d2U+j/26vUrbzBQPF91wuOdSRAcxs0Cnxkr4hP630/zljPThg6xd/JjcOK/8g1qv8veQMyQXgknB/qndZdSsanh5f8mx16/iOZeFIrPWHdim0dOVR36JMAflWmaw7iLJ8PuPqThCGQ5U7sYbXKL9h+cwhtnWQuo+Nv8spuPgryEUFwC4fkii3YX2hhFqe8LNv7uc31E+MkwSMznT/QtzAOCyygTjUGzhAPXIW2YXyMRnKH6Bm9dmqu9kgHSig5TyJnzHw915F2UMmICLQjQlTZAMcTSN58mFE1+i5tLdfbQX+I7sCCnciCEtv+CHxHCXkaESxUazfYrl617YzVFfce9albCRTFSQS+FhRBTbbqxfLS3axSNnpi97XifmVouqdDs35psu12c57WEviCt13SuxtbFGSCDu9wbarwA==212FD3x19z9sWBHDJACbC00B75E	kATrbm+rtLDD6/6yNADNF/dcwUt5+WNxRD9zjGgLjNYEON8PMJ+j5mazedr8wX/3gwSD9DPkRRZazilS0XqlWh7gTltcmW2pJV8jmz6YdiVOV3eA7ghBsATXkkQ9JafPdkYC35P8gnhawf7C8wd/VoSRvqbwT0Hl6TYkFeh1qhg5pfxWMv8GKcFsfPMztYPKglgPqeY8fRRkBSEuE2DK+iSdREAdeFZ8snKHL1DIwB+DD9qW292xNy5V5/6oZFdjMLGA7aKsFTp8hwWaJsd1bCcQ6GHdknU+e7HzRYDhKyV7SJp/wCuCR5o2dDigyQi6cynmc/Tg6mdTiR6MQ889nucV0yZXqzZvoh3vvoKEKtcXM4uoykrbAlrX6FoqgJSuZ1lciPDPFCvkctGZh8oLLBE24Tfo4q7HBGHP6XgZEFA1xoLEXrTqw44bkrn100MQuG4LYrgoVi/JHHvlcPvokixrL326mloytAAbOgqWDpTG4uSmd05ZBb6/N1N7J8nnwzyWxR/kjshTqBHmZsytUrzhKm9PxWCoQT/6aZXkAIePMCN1b+UII0IRgnvnSPgmHVAPHamcDRt1eM77sXPOTBY7ln0W8N/f/gDUqMadISjInADoDeqAr8DAAFPseXIMSfPlluyZBm7J5cFDPol2gUYmlEPKYmQAZyZX99V5PWOoGoHwG/47yl3dkhcN9PzDs3Gd5NbVgjSGoHUWFi4aJLP8ROv3Ho24IXB1+/zRBjbDp8AjB0woB9wDSXmkgW3pP2HSHXcH3CJpTLnVXtT9AEnprvV8FZkokTBV922UFw3E4AlVGRCSR2lJxVoI85wc030REq6yB24WrFkyUFONourSyXKO7GbWWRLZU9SLF1CfcEGTJiU2xaIAirdD6CNoGmyDZaBzhm4=212FD3x19z9sWBHDJACbC00B75E	1562956704394
\.


--
-- Name: auth_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_tokens_id_seq', 2, true);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, password) FROM stdin;
1	testaccount	otsosika
2	amazonka27	otsosika1
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: auth_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT auth_tokens_pkey PRIMARY KEY (id);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: auth_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT auth_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

