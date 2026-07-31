"""
Example: How to integrate DesktopAnalyzer with OMEGA agent.
"""

from desktop_analyzer import DesktopAnalyzer, AnalyzerConfig
from pathlib import Path
import json


class OmegaWorkspaceAnalyzer:
    """OMEGA agent workspace analyzer integration."""

    def __init__(self, workspace_paths: list[str]):
        """Initialize with workspace paths."""
        self.config = AnalyzerConfig(
            target_paths=workspace_paths,
            output_format='json',  # Use JSON for structured data
            max_depth=3,
            max_files_per_dir=15
        )
        self.analyzer = DesktopAnalyzer(self.config)
        self.result = None

    def analyze_workspace(self) -> dict:
        """Analyze workspace and return structured context for agent."""
        self.result = self.analyzer.analyze()

        return {
            "timestamp": self.result.timestamp,
            "workspace_summary": {
                "total_folders": self.result.total_folders,
                "valid_folders": self.result.valid_folders,
                "total_files": self.result.total_files,
                "valid_percentage": (
                    self.result.valid_folders / max(self.result.total_folders, 1) * 100
                )
            },
            "structure": self._extract_structure(),
            "projects": self._extract_projects(),
            "file_types": self._extract_file_types()
        }

    def _extract_structure(self) -> dict:
        """Extract folder structure organized by level."""
        structure = {"by_level": {}}

        for folder in self.result.folders:
            level = folder.level
            if level not in structure["by_level"]:
                structure["by_level"][level] = []

            structure["by_level"][level].append({
                "name": folder.name,
                "path": folder.path,
                "status": folder.status,
                "is_valid_jd": folder.is_valid_jd,
                "is_valid_para": folder.is_valid_para,
                "file_count": len(folder.files)
            })

        return structure

    def _extract_projects(self) -> list[dict]:
        """Extract valid projects (JD and PARA)."""
        projects = []

        for folder in self.result.folders:
            if folder.status == "✅":  # Valid folder
                projects.append({
                    "name": folder.name,
                    "path": folder.path,
                    "type": "johnny_decimal" if folder.is_valid_jd else "para",
                    "files": [
                        {"name": f.name, "extension": f.extension}
                        for f in folder.files
                    ]
                })

        return projects

    def _extract_file_types(self) -> dict:
        """Extract file type statistics."""
        file_types = {}

        for folder in self.result.folders:
            for file in folder.files:
                ext = file.extension or "no_extension"
                if ext not in file_types:
                    file_types[ext] = 0
                file_types[ext] += 1

        return dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True))

    def get_agent_context(self) -> str:
        """Get human-readable context for OMEGA agent."""
        if not self.result:
            self.analyze_workspace()

        context = f"""
# OMEGA WORKSPACE ANALYSIS

## Summary
- **Total Folders**: {self.result.total_folders}
- **Valid Folders**: {self.result.valid_folders}
- **Total Files**: {self.result.total_files}
- **Analysis Time**: {self.result.timestamp}

## Valid Projects (Ready for Work)
"""
        for folder in self.result.folders:
            if folder.status == "✅":
                context += f"\n- **{folder.name}** ({folder.path})"
                if folder.files:
                    context += f"\n  - Files: {', '.join([f.name for f in folder.files[:5]])}"
                    if len(folder.files) > 5:
                        context += f" (+{len(folder.files) - 5} more)"

        context += f"\n\n## File Types\n"
        for ext, count in list(self._extract_file_types().items())[:10]:
            context += f"- {ext}: {count}\n"

        return context

    def get_json_context(self) -> str:
        """Get JSON context for OMEGA agent API."""
        return json.dumps(self.analyze_workspace(), indent=2, ensure_ascii=False)


# Example usage
if __name__ == "__main__":
    # Example 1: Basic integration
    print("=" * 60)
    print("OMEGA DESKTOP ANALYZER - INTEGRATION EXAMPLE")
    print("=" * 60)

    # Initialize with workspace paths
    analyzer = OmegaWorkspaceAnalyzer(
        workspace_paths=[
            "/home/user/desktop-analyzer",
            "/tmp"  # Additional path
        ]
    )

    # Get structured context for agent
    context = analyzer.analyze_workspace()
    print("\n✅ Workspace Analysis Complete")
    print(f"   - Folders: {context['workspace_summary']['total_folders']}")
    print(f"   - Valid: {context['workspace_summary']['valid_folders']}")
    print(f"   - Files: {context['workspace_summary']['total_files']}")

    # Get human-readable context
    print("\n" + "=" * 60)
    print("AGENT CONTEXT (Human-Readable)")
    print("=" * 60)
    print(analyzer.get_agent_context())

    # Get JSON for API
    print("\n" + "=" * 60)
    print("AGENT CONTEXT (JSON)")
    print("=" * 60)
    print(analyzer.get_json_context()[:500] + "...")
