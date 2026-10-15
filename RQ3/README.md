# Research Question 3: Human Evaluation of PR Link Ranking Approach

This folder contains the data and context relevant to **Research Question 3 (RQ3)**, which focuses on evaluating human feedback and developer perception of our PR link ranking tools.

## 🛠️ Interactive Tool Showcase
To conduct this evaluation, we built a separate showcase repository. This environment allows users to simulate creating a pull request themselves and observe how our tool ranks the included links in real-time.
* **Showcase Repository:** [c4rtune/toolsShowcaseTemp](https://github.com/c4rtune/toolsShowcaseTemp)

---

## 🧪 Evaluation Methodology
During the human evaluation sessions, participants were guided through the following process:

1. **Demonstration:** We first demonstrated how the tool functions using a real-world pull request as a baseline example (`rust-lang/rust#60785`).
2. **Participant Trial:** Next, participants were asked to test the tool hands-on by replicating the link structure of another specific pull request (`electron/electron#25522`).
3. **Feedback Survey:** After completing the trial, participants were asked to fill out an evaluation survey to capture their qualitative and quantitative feedback on the system.

---

## 📋 Evaluation Surveys
The post-evaluation survey was distributed via Google Forms and made available in two languages:
* **English Version:** [Take the Survey (English)](https://docs.google.com/forms/d/e/1FAIpQLSf3B4zB_d4swd0LNBOnFsy_yQBH-HzPb6hDMfXCiMnAvAxVKQ/viewform?usp=dialog)
* **Thai Version:** [Take the Survey (Thai)](https://docs.google.com/forms/d/e/1FAIpQLScbaE7-FHcRuIj12JeIYPwIdz7XK_oJDs4xXo5pxGu9kYmqyg/viewform?usp=dialog)

---

## 📊 Results Data
### `survey_responses_deidentified.csv`
The survey responses of the 14 participants, one row per participant, collected after they completed the tool showcase and evaluation. The responses were de-identified for this release:
* Submission timestamps were removed.
* The consent statement was removed (all participants gave consent).
* Participants are identified only by an ID assigned in this release (`P01`–`P14`).

Likert answers keep the original labels (e.g., `4 - Good`). Some free-text comments are in Thai, as participants could answer in either language.

### `survey_codebook.csv`
Maps each column of the responses file to its survey section and the full question text. The SUS columns `sus_q1`–`sus_q10` follow the standard System Usability Scale order: odd items are positively worded, even items negatively worded.
