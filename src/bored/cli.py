from __future__ import annotations

from typing import NamedTuple

import typer

import gum
from bored.models import Activity
from bored.store import ActivityStore


class ActivityCLI(NamedTuple):
    activity_store: ActivityStore

    def list(self) -> None:
        for activity in self.activity_store.data.values():
            typer.echo(f"{activity.title}: {activity.description}")

    def add(self) -> None:
        activity: str = input("Title: ")
        description: str = gum.gum_write({"header": "Description"})
        activity_obj = Activity.create_activity(title=activity, description=description)
        self.activity_store.add(activity_obj)
        typer.echo(f"Added activity: {activity_obj.id}")

    def delete(self) -> None:
        selected: Activity | None = gum.gum_choose(  # type:ignore[call-overload]
            self.activity_store.data.values(),
            key=lambda x: f"{x.title}: {x.description}",
            multi=False,
        )
        if selected:
            self.activity_store.remove(selected)
            typer.echo(f"Deleted activity: {selected.title}")

    def get_app(self) -> typer.Typer:
        app = typer.Typer()
        app.command()(self.list)
        app.command()(self.add)
        app.command()(self.delete)
        return app


activity_store = ActivityStore("activities.pickle")
activity_cli = ActivityCLI(activity_store)
app = activity_cli.get_app()

if __name__ == "__main__":
    app()
