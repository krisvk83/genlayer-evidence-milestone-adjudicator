# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
from dataclasses import dataclass
import time


@allow_storage
@dataclass
class Milestone:
    title: str
    criteria: str
    evidence_url: str
    min_score: u32
    deadline: u64
    status: str
    submitter: str
    decision: str
    score: i64
    reason: str
    checked_at: u64


class EvidenceMilestoneAdjudicator(gl.Contract):

    owner: str
    milestones: TreeMap[str, Milestone]

    def __init__(self):
        self.owner = str(gl.message.sender_address)

    def _require_owner(self):
        if str(gl.message.sender_address) != self.owner:
            raise gl.vm.UserError(
                "only owner may create, reopen, or cancel milestones"
            )

    @gl.public.write
    def create_milestone(
        self,
        milestone_id: str,
        title: str,
        criteria: str,
        evidence_url: str,
        min_score: u32,
        deadline: u64,
    ) -> None:

        self._require_owner()

        if not milestone_id:
            raise gl.vm.UserError("milestone_id cannot be empty")

        if milestone_id in self.milestones:
            raise gl.vm.UserError("milestone already exists")

        if not title.strip():
            raise gl.vm.UserError("title cannot be empty")

        if not criteria.strip():
            raise gl.vm.UserError("criteria cannot be empty")

        if not evidence_url.startswith(("http://", "https://")):
            raise gl.vm.UserError("evidence_url must be http(s)")

        if min_score > 100:
            raise gl.vm.UserError(
                "min_score must be between 0 and 100"
            )

        if deadline <= u64(int(time.time())):
            raise gl.vm.UserError(
                "deadline must be in the future"
            )

        self.milestones[milestone_id] = Milestone(
            title=title,
            criteria=criteria,
            evidence_url=evidence_url,
            min_score=min_score,
            deadline=deadline,
            status="OPEN",
            submitter="",
            decision="",
            score=-1,
            reason="",
            checked_at=0,
        )

    @gl.public.write
    def submit_milestone(
        self,
        milestone_id: str,
    ) -> None:

        if milestone_id not in self.milestones:
            raise gl.vm.UserError("unknown milestone")

        milestone = self.milestones[milestone_id]

        if milestone.status != "OPEN":
            raise gl.vm.UserError(
                "milestone is not open"
            )

        now = u64(int(time.time()))

        if now > milestone.deadline:
            raise gl.vm.UserError(
                "submission deadline has passed"
            )

        submitter = str(gl.message.sender_address)

        title = milestone.title
        criteria = milestone.criteria
        evidence_url = milestone.evidence_url
        min_score = milestone.min_score

        def evaluate():

            page = gl.nondet.web.render(
                evidence_url,
                mode="text"
            )

            prompt = f"""
You are an evidence adjudicator for a blockchain milestone.

MILESTONE:
{title}

ACCEPTANCE CRITERIA:
{criteria}

MINIMUM SCORE:
{min_score}/100

PUBLIC EVIDENCE URL:
{evidence_url}

EVIDENCE PAGE:
{page}

Evaluate ONLY whether the evidence demonstrates that the
milestone satisfies the stated acceptance criteria.

Do not invent facts.
Do not rely on information outside the supplied evidence.

Return JSON only:

{{
  "decision": "ACCEPT" or "REJECT",
  "score": integer from 0 to 100,
  "reason": "brief evidence-grounded explanation"
}}

SCORING:

90-100:
The evidence clearly satisfies the criteria.

70-89:
The evidence substantially satisfies the criteria
but contains a material deficiency.

0-69:
The evidence does not sufficiently satisfy the criteria.

DECISION:

Return ACCEPT only if:

1. The evidence actually supports the criteria, AND
2. The score is at least {min_score}.

Otherwise return REJECT.
"""

            return gl.nondet.exec_prompt(
                prompt,
                response_format="json"
            )

        result = gl.eq_principle.prompt_comparative(
            evaluate,
            principle=(
                "The decision field must match exactly. "
                "The score must be within 5 points. "
                "Both answers must evaluate the same public "
                "evidence against the same acceptance criteria. "
                "Reasoning may differ. Unsupported or invented "
                "facts must not be accepted."
            ),
        )

        if not isinstance(result, dict):
            raise gl.vm.UserError(
                "adjudication returned invalid data"
            )

        decision = result.get("decision")
        score = result.get("score")
        reason = result.get("reason", "")

        if decision not in ("ACCEPT", "REJECT"):
            raise gl.vm.UserError(
                "invalid adjudication decision"
            )

        if not isinstance(score, int):
            raise gl.vm.UserError(
                "invalid adjudication score"
            )

        if score < 0 or score > 100:
            raise gl.vm.UserError(
                "adjudication score must be between 0 and 100"
            )

        final_decision = (
            "ACCEPT"
            if decision == "ACCEPT"
            and score >= int(min_score)
            else "REJECT"
        )

        milestone.status = (
            "ACCEPTED"
            if final_decision == "ACCEPT"
            else "REJECTED"
        )

        milestone.submitter = submitter
        milestone.decision = final_decision
        milestone.score = score
        milestone.reason = str(reason)[:1000]
        milestone.checked_at = now

        # Persist the modified milestone back into the TreeMap.
        self.milestones[milestone_id] = milestone

    @gl.public.write
    def reopen_milestone(
        self,
        milestone_id: str,
    ) -> None:

        self._require_owner()

        if milestone_id not in self.milestones:
            raise gl.vm.UserError("unknown milestone")

        milestone = self.milestones[milestone_id]

        if milestone.status not in ("ACCEPTED", "REJECTED"):
            raise gl.vm.UserError(
                "milestone is not resolved"
            )

        milestone.status = "OPEN"
        milestone.submitter = ""
        milestone.decision = ""
        milestone.score = -1
        milestone.reason = ""
        milestone.checked_at = 0

        self.milestones[milestone_id] = milestone

    @gl.public.write
    def cancel_milestone(
        self,
        milestone_id: str,
    ) -> None:

        self._require_owner()

        if milestone_id not in self.milestones:
            raise gl.vm.UserError("unknown milestone")

        milestone = self.milestones[milestone_id]

        if milestone.status != "OPEN":
            raise gl.vm.UserError(
                "only open milestones can be cancelled"
            )

        milestone.status = "CANCELLED"

        self.milestones[milestone_id] = milestone

    @gl.public.view
    def get_milestone(
        self,
        milestone_id: str,
    ) -> dict:

        if milestone_id not in self.milestones:
            raise gl.vm.UserError("unknown milestone")

        milestone = self.milestones[milestone_id]

        return {
            "title": milestone.title,
            "criteria": milestone.criteria,
            "evidence_url": milestone.evidence_url,
            "min_score": int(milestone.min_score),
            "deadline": int(milestone.deadline),
            "status": milestone.status,
            "submitter": milestone.submitter,
            "decision": milestone.decision,
            "score": int(milestone.score),
            "reason": milestone.reason,
            "checked_at": int(milestone.checked_at),
        }

    @gl.public.view
    def get_status(
        self,
        milestone_id: str,
    ) -> str:

        if milestone_id not in self.milestones:
            raise gl.vm.UserError("unknown milestone")

        return self.milestones[milestone_id].status

    @gl.public.view
    def get_owner(self) -> str:
        return self.owner
