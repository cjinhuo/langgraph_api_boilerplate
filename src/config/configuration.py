from dataclasses import dataclass, field
from typing import Optional, Any
from langchain_core.runnables import RunnableConfig
import os
from dataclasses import fields


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields."""

    # resources: list[Resource] = field(
    #     default_factory=list
    # )  # Resources to be used for the research
    max_plan_iterations: int = 1  # Maximum number of plan iterations
    max_step_num: int = 3  # Maximum number of steps in a plan
    max_search_results: int = 3  # Maximum number of search results
    # mcp_settings: dict = None  # MCP settings, including dynamic loaded tools
    # report_style: str = ReportStyle.ACADEMIC.value  # Report style
    enable_deep_thinking: bool = False  # Whether to enable deep thinking
    enforce_web_search: bool = (
        False  # Enforce at least one web search step in every plan
    )
    enforce_researcher_search: bool = (
        True  # Enforce that researcher must use web search tool at least once
    )
    interrupt_before_tools: list[str] = field(
        default_factory=list
    )  # List of tool names to interrupt before execution

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})
