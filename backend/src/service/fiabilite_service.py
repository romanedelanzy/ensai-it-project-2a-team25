
from datetime import datetime

from dao.StationStatusDAO import StationStatusDao


class ReliabilityService:
    """ Service qui calcule la fiabilite d'une station a partir de l'historique."""

    def _percent_time_in_state(
        self,
        history,
        state_type: str,
        end_date: datetime | None = None,
    ) -> float:
        """Calcule la proportion de temps passée dans un état donné."""

        if not history:
            return 0.0

        if end_date is None:
            end_date = history[-1].horodatage

        total_duration = (
            end_date - history[0].horodatage
        ).total_seconds()

        if total_duration <= 0:
            return 0.0

        state_start = None
        state_duration = 0

        for status in history:

            if state_type == "empty":
                is_in_state = status.is_empty()

            elif state_type == "saturated":
                is_in_state = status.is_saturated()

            else:
                raise ValueError("Etat inconnu")

            if is_in_state:
                if state_start is None:
                    state_start = status.horodatage

            else:
                if state_start is not None:
                    duration = (
                        status.horodatage - state_start
                    ).total_seconds()
                    state_duration += duration
                    state_start = None

        if state_start is not None:
            duration = (end_date - state_start).total_seconds()
            state_duration += duration

        return state_duration / total_duration

    def percent_time_empty_all(self, id_station: str) -> float:
        """Pourcentage de temps ou une station est vide sur tout l'historique"""

        history = StationStatusDao().find_all_history(id_station)

        return self._percent_time_in_state(history, "empty")

    def percent_time_empty_until(self, id_station: str, end: datetime) -> float:
        """Poucentage de temps ou une station est vide jusqu'a une certaine date"""

        history = StationStatusDao().find_history_until(id_station, end)

        return self._percent_time_in_state(history, "empty", end)

    def percent_saturation_all(self, id_station: str) -> float:
        """Pourcentage de temps ou une station est saturee sur tout l'historique"""

        history = StationStatusDao().find_all_history(id_station)

        return self._percent_time_in_state(history, "saturated")

    def percent_saturation_until(self, id_station: str, end: datetime) -> float:
        """Pourcentage de temps ou une station est saturee jusqu'à une date"""

        history = StationStatusDao().find_history_until(id_station, end)

        return self._percent_time_in_state(history, "saturated", end)

    def _average_duration_in_state(
        self,
        history,
        state_type: str,
        end_date: datetime | None = None,
    ) -> float | None:
        """Calcule la durée moyenne des épisodes d'un état en heures."""

        if not history:
            return None

        if end_date is None:
            end_date = history[-1].horodatage

        state_start = None
        state_durations = []

        for status in history:

            if state_type == "empty":
                is_in_state = status.is_empty()

            elif state_type == "saturated":
                is_in_state = status.is_saturated()

            else:
                raise ValueError("Etat inconnu")

            if is_in_state:
                if state_start is None:
                    state_start = status.horodatage

            else:
                if state_start is not None:
                    duration = status.horodatage - state_start
                    state_durations.append(duration.total_seconds() / 3600)
                    state_start = None

        # Si l'episode est toujours en cours à la date de fin
        if state_start is not None:
            duration = end_date - state_start
            state_durations.append(duration.total_seconds() / 3600)

        if not state_durations:
            return 0

        return sum(state_durations) / len(state_durations)

    def average_empty_duration_all(self, station_id: str) -> float | None:
        """ Pour l'historique entier, calcule la duree moyenne des episodes de
        vide pour une station.
        """

        history = StationStatusDao().find_all_history(station_id)

        return self._average_duration_in_state(history, "empty")

    def average_saturated_duration_all(self, station_id: str) -> float | None:
        """ Pour l'historique entier, calcule la duree moyenne des episodes de
        saturation pour une station.
        """

        history = StationStatusDao().find_all_history(station_id)

        return self._average_duration_in_state(history, "saturated")

    def average_empty_duration_until(
        self,
        station_id: str,
        end_date: datetime,
    ) -> float | None:
        """En heures, donne la duree moyenne où une station est vide jusqu'a une
        certaine date
        """

        history = StationStatusDao().find_history_until(station_id, end_date)

        return self._average_duration_in_state(history, "empty", end_date)

    def average_saturated_duration_until(
        self,
        station_id: str,
        end_date: datetime,
    ) -> float | None:
        """Donne en heure la duree moyenne des episodes de saturation d'une
        station jusqu'a une certaine date
        """

        history = StationStatusDao().find_history_until(station_id, end_date)

        return self._average_duration_in_state(
            history, "saturated", end_date
        )

    def _calculate_score(
        self,
        current_score: float,
        percent_empty: float,
        percent_saturated: float,
        mean_time_empty: float | None,
        mean_time_saturated: float | None,
        total_duration_hours: float,
    ) -> float:
        """Calcule le score à partir des indicateurs déjà calculés."""

        if mean_time_empty is None:
            score_empty_duration = 0.5
        else:
            score_empty_duration = 1 - mean_time_empty / total_duration_hours

        if mean_time_saturated is None:
            score_saturated_duration = 0.5
        else:
            score_saturated_duration = (
                1 - mean_time_saturated / total_duration_hours
            )

        score = (
            current_score
            + (1 - percent_empty)
            + (1 - percent_saturated)
            + score_empty_duration
            + score_saturated_duration
        ) / 5

        return score

    def reliability_current_score(self, id_station: str) -> float:

        dao = StationStatusDao()
        history = dao.find_all_history(id_station)

        if not history:
            return 0.0

        total_duration = history[-1].horodatage - history[0].horodatage
        total_duration_hours = total_duration.total_seconds() / 3600

        if total_duration_hours <= 0:
            return 0.0

        current_status = dao.find_current_status(id_station)

        if current_status is None:
            current_score = 0.5
        elif not current_status.is_empty() and not current_status.is_saturated():
            current_score = 1
        else:
            current_score = 0

        percent_empty = self._percent_time_in_state(history, "empty")
        percent_saturated = self._percent_time_in_state(history, "saturated")

        mean_time_empty = self._average_duration_in_state(history, "empty")
        mean_time_saturated = self._average_duration_in_state(
            history, "saturated"
        )

        return self._calculate_score(
            current_score,
            percent_empty,
            percent_saturated,
            mean_time_empty,
            mean_time_saturated,
            total_duration_hours,
        )

    def reliability_score_evolution(self, id_station: str) -> dict[datetime, float]:
        """Calcule l'evolution du score de fiabilite d'une station au cours du temps."""

        history = StationStatusDao().find_all_history(id_station)

        scores = {}

        if not history:
            return scores

        first_date = history[0].horodatage

        # Compteurs cumulés
        empty_duration = 0
        saturated_duration = 0

        empty_episode_durations = []
        saturated_episode_durations = []

        empty_start = None
        saturated_start = None

        previous_status = history[0]

        # Initialisation des épisodes éventuels
        if previous_status.is_empty():
            empty_start = first_date

        if previous_status.is_saturated():
            saturated_start = first_date

        for i, current_status in enumerate(history):

            current_date = current_status.horodatage

            total_duration = current_date - first_date
            total_duration_hours = total_duration.total_seconds() / 3600

            if total_duration_hours <= 0:
                scores[current_date] = 0.0
                continue

            # Mise à jour des durées cumulées entre deux dates
            if i > 0:

                interval_duration = (
                    current_date - previous_status.horodatage
                ).total_seconds()

                # L'intervalle est attribué à l'état précédent
                if previous_status.is_empty():
                    empty_duration += interval_duration

                if previous_status.is_saturated():
                    saturated_duration += interval_duration

            # Gestion des épisodes de vide
            if current_status.is_empty():

                if empty_start is None:
                    empty_start = current_date

            else:

                if empty_start is not None:
                    episode_duration = (
                        current_date - empty_start
                    ).total_seconds() / 3600

                    empty_episode_durations.append(episode_duration)
                    empty_start = None

            # Gestion des épisodes de saturation
            if current_status.is_saturated():

                if saturated_start is None:
                    saturated_start = current_date

            else:

                if saturated_start is not None:
                    episode_duration = (
                        current_date - saturated_start
                    ).total_seconds() / 3600

                    saturated_episode_durations.append(episode_duration)
                    saturated_start = None

            # Pourcentages de temps vide et sature jusqu'a la date courante
            total_duration_seconds = total_duration.total_seconds()

            percent_empty = empty_duration / total_duration_seconds
            percent_saturated = saturated_duration / total_duration_seconds

            # Durees moyennes des episodes vides et satures jusqu'a la date courante
            current_empty_durations = empty_episode_durations.copy()

            if empty_start is not None:
                current_empty_durations.append(
                    (current_date - empty_start).total_seconds() / 3600
                )

            current_saturated_durations = saturated_episode_durations.copy()

            if saturated_start is not None:
                current_saturated_durations.append(
                    (current_date - saturated_start).total_seconds() / 3600
                )

            if current_empty_durations:
                mean_time_empty = (
                    sum(current_empty_durations) / len(current_empty_durations)
                )
            else:
                mean_time_empty = 0

            if current_saturated_durations:
                mean_time_saturated = (
                    sum(current_saturated_durations)
                    / len(current_saturated_durations)
                )
            else:
                mean_time_saturated = 0

            # Score de l'etat actuel
            if not current_status.is_empty() and not current_status.is_saturated():
                current_score = 1
            else:
                current_score = 0

            score = self._calculate_score(
                current_score,
                percent_empty,
                percent_saturated,
                mean_time_empty,
                mean_time_saturated,
                total_duration_hours,
            )

            scores[current_date] = score

            previous_status = current_status

        return scores
