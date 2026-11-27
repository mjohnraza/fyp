import re
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SkillDefinition(BaseModel):
    name: str
    description: str
    instructions: str
    source_path: str


class SkillLoader:
    """Discovers and loads Antigravity SKILL.md files from .agents/skills/."""

    def __init__(self, skills_root: Optional[Path] = None):
        if skills_root is None:
            # Resolve project root: src/agentic_os/runtime/skill_loader.py -> 4 parents up
            skills_root = Path(__file__).resolve().parent.parent.parent.parent / ".agents" / "skills"
        self.skills_root = skills_root
        self._skills: Dict[str, SkillDefinition] = {}
        self.discover_skills()

    def discover_skills(self) -> Dict[str, SkillDefinition]:
        self._skills.clear()
        if not self.skills_root.exists():
            return self._skills

        for skill_file in self.skills_root.glob("*/SKILL.md"):
            parsed = self._parse_skill_md(skill_file)
            if parsed:
                self._skills[parsed.name] = parsed
        return self._skills

    def _parse_skill_md(self, path: Path) -> Optional[SkillDefinition]:
        content = path.read_text(encoding="utf-8")
        name = path.parent.name
        description = ""
        instructions = content

        # Parse YAML frontmatter if present
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if fm_match:
            frontmatter = fm_match.group(1)
            instructions = fm_match.group(2).strip()
            for line in frontmatter.splitlines():
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("description:"):
                    description = line.split(":", 1)[1].strip().strip('"').strip("'")

        return SkillDefinition(
            name=name,
            description=description,
            instructions=instructions,
            source_path=str(path)
        )

    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        return self._skills.get(name)

    def list_skills(self) -> List[SkillDefinition]:
        return list(self._skills.values())

    def render_system_prompt(self, skill_names: List[str]) -> str:
        """Builds a system prompt combining the selected SKILL.md instructions."""
        sections = []
        for s_name in skill_names:
            skill = self.get_skill(s_name)
            if skill:
                sections.append(f"## Active Skill: {skill.name}\n{skill.instructions}")
        return "\n\n---\n\n".join(sections)
