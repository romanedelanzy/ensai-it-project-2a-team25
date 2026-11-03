
from datetime import datetime

from dao.StationStatusDAO import StationStatusDao


class ReliabilityService:
    """ Service qui calcule la fiabilite d'une station a partir de l'historique."""

    def percent_time_empty_all(self, id_station: str) -> float:
        """Pourcentage de temps ou une station est vide sur tout l'historique"""

        history = StationStatusDao().find_all_history(id_station)

        if not history:
            return 0.0

        total_duration = (
            history[-1].horodatage - history[0].horodatage
        ).total_seconds()

        if total_duration <= 0:
            return 0.0

        empty_start = None
        empty_duration = 0

        for status in history:
            if status.is_empty():
                if empty_start is None:
                    empty_start = status.horodatage

            else:
                if empty_start is not None:
                    duration = status.horodatage - empty_start
                    empty_duration += duration.total_seconds()
                    empty_start = None

        if empty_start is not None:
            duration = history[-1].horodatage - empty_start
            empty_duration += duration.total_seconds()

        return empty_duration / total_duration

    def percent_time_empty_until(self, id_station: str, end: datetime) -> float:
        """Poucentage de temps ou une station est vide jusqu'a une certaine date"""

        history = StationStatusDao().find_history_until(id_station, end)

        if not history:
            return 0.0

        total_duration = (
            end - history[0].horodatage
        ).total_seconds()

        if total_duration <= 0:
            return 0.0

        empty_start = None
        empty_duration = 0

        for status in history:
            if status.is_empty():
                if empty_start is None:
                    empty_start = status.horodatage

            else:
                if empty_start is not None:
                    duration = status.horodatage - empty_start
                    empty_duration += duration.total_seconds()
                    empty_start = None

        if empty_start is not None:
            duration = end - empty_start
            empty_duration += duration.total_seconds()

        return empty_duration / total_duration

    def percent_saturation_all(self, id_station: str) -> float:
        """Pourcentage de temps ou une station est saturee sur tout l'historique"""

        history = StationStatusDao().find_all_history(id_station)

        if not history:
            return 0.0

        total_duration = (
            history[-1].horodatage - history[0].horodatage
        ).total_seconds()

        if total_duration <= 0:
            return 0.0

        sat_start = None
        sat_duration = 0

        for status in history:
            if status.is_saturated():
                if sat_start is None:
                    sat_start = status.horodatage

            else:
                if sat_start is not None:
                    duration = status.horodatage - sat_start
                    sat_duration += duration.total_seconds()
                    sat_start = None

        if sat_start is not None:
            duration = history[-1].horodatage - sat_start
            sat_duration += duration.total_seconds()

        return sat_duration / total_duration

    def percent_saturation_until(self, id_station: str, end: datetime) -> float:
        """Pourcentage de temps ou une station est saturee jusqu'à une certaine date"""

        history = StationStatusDao().find_history_until(id_station, end)

        if not history:
            return 0.0

        total_duration = (
            end - history[0].horodatage
        ).total_seconds()

        if total_duration <= 0:
            return 0.0

        sat_start = None
        sat_duration = 0

        for status in history:
            if status.is_saturated():
                if sat_start is None:
                    sat_start = status.horodatage

            else:
                if sat_start is not None:
                    duration = status.horodatage - sat_start
                    sat_duration += duration.total_seconds()
                    sat_start = None

        if sat_start is not None:
            duration = end - sat_start
            sat_duration += duration.total_seconds()

        return sat_duration / total_duration

    def average_empty_duration_all(self, station_id: str) -> float | None:
        """ Pour l'historique entier, calcule la duree moyenne des episodes de
        saturation pour une station.
        """

        history = StationStatusDao().find_all_history(station_id)

        if not history:
            return None

        empty_start = None
        empty_durations = []

        for status in history:

            if status.is_empty():
                if empty_start is None:
                    empty_start = status.horodatage

            else:
                if empty_start is not None:
                    duration = status.horodatage - empty_start
                    empty_durations.append(duration.total_seconds() / 3600)
                    empty_start = None

        # Si la station est toujours vide 
        if empty_start is not None:
            # On prend la derniere date
            duration = history[-1].horodatage - empty_start
            empty_durations.append(duration.total_seconds() / 3600)

        if not empty_durations:
            return 0

        return sum(empty_durations) / len(empty_durations)

    def average_saturated_duration_all(self, station_id: str) -> float | None:
        """ Pour l'historique entier, calcule la duree moyenne des episodes de
        saturation pour une station.
        """

        history = StationStatusDao().find_all_history(station_id)

        if not history:
            return None

        sat_start = None
        sat_durations = []

        for status in history:

            if status.is_saturated():
                if sat_start is None:
                    sat_start = status.horodatage

            else:
                if sat_start is not None:
                    duration = status.horodatage - sat_start
                    sat_durations.append(duration.total_seconds() / 3600)
                    sat_start = None

        # Si la station est toujours saturée 
        if sat_start is not None:
            # On prend la derniere date
            duration = history[-1].horodatage - sat_start
            sat_durations.append(duration.total_seconds() / 3600)

        if not sat_durations:
            return 0

        return sum(sat_durations) / len(sat_durations)

    def average_empty_duration_until(self, station_id: str, end_date: datetime) -> float | None:
        """En heures, donne la duree moyenne où une station est vide jusqu'a une
        certaine date
        """

        history = StationStatusDao().find_history_until(station_id, end_date)

        if not history:
            return None

        empty_start = None
        empty_durations = []

        for status in history:

            if status.is_empty():
                if empty_start is None:
                    empty_start = status.horodatage

            else:
                if empty_start is not None:
                    duration = status.horodatage - empty_start
                    empty_durations.append(duration.total_seconds() / 3600)
                    empty_start = None

        # Si la station est toujours vide à la date de fin
        if empty_start is not None:
            duration = end_date - empty_start
            empty_durations.append(duration.total_seconds() / 3600)

        if not empty_durations:
            return 0

        return sum(empty_durations) / len(empty_durations)

    def average_saturated_duration_until(self, station_id: str, end_date: datetime) -> float | None:
        """Donne en heure la duree moyenne des episodes de saturations d'une
        station jusqu'a une certaine date
        """

        history = StationStatusDao().find_history_until(station_id, end_date)

        if not history:
            return None

        sat_start = None
        sat_durations = []

        for status in history:

            if status.is_saturated():
                if sat_start is None:
                    sat_start = status.horodatage

            else:
                if sat_start is not None:
                    duration = status.horodatage - sat_start
                    sat_durations.append(duration.total_seconds() / 3600)
                    sat_start = None

        # Si la station est toujours saturée à la date de fin
        if sat_start is not None:
            duration = end_date - sat_start
            sat_durations.append(duration.total_seconds() / 3600)

        if not sat_durations:
            return 0

        return sum(sat_durations) / len(sat_durations)

    def reliability_current_score(self, id_station: str) -> float:

        history = StationStatusDao().find_all_history(id_station)

        if not history:
            return 0.0

        total_duration = history[-1].horodatage - history[0].horodatage
        total_duration_hours = total_duration.total_seconds() / 3600

        if total_duration_hours <= 0:
            return 0.0

        current_status = StationStatusDao().find_current_status(id_station)

        if current_status is None:
            current_score = 0.5
        elif not current_status.is_empty() and not current_status.is_saturated():
            current_score = 1
        else:
            current_score = 0

        percent_empty = self.percent_time_empty_all(id_station)
        percent_saturated = self.percent_saturation_all(id_station)

        mean_time_empty = self.average_empty_duration_all(id_station)
        mean_time_saturated = self.average_saturated_duration_all(id_station)

        if mean_time_empty is None:
            score_empty_duration = 0.5
        else:
            score_empty_duration = 1 - mean_time_empty / total_duration_hours

        if mean_time_saturated is None:
            score_saturated_duration = 0.5
        else:
            score_saturated_duration = 1 - mean_time_saturated / total_duration_hours

        score = (
            current_score
            + (1 - percent_empty)
            + (1 - percent_saturated)
            + score_empty_duration
            + score_saturated_duration
        ) / 5

        return score

    def reliability_score_evolution(self, id_station: str) -> dict[datetime, float]:
        """Calcule l'evolution du score de fiabilite d'une station au cours du temps."""

        history = StationStatusDao().find_all_history(id_station)

        scores = {}

        if not history:
            return scores

        first_date = history[0].horodatage

        for current_status in history:

            current_date = current_status.horodatage

            total_duration = current_date - first_date
            total_duration_hours = total_duration.total_seconds() / 3600

            if total_duration_hours <= 0:
                scores[current_date] = 0.0
                continue

            # Score de l'etat actuel
            if not current_status.is_empty() and not current_status.is_saturated():
                current_score = 1
            else:
                current_score = 0

            # Pourcentages de temps vide et sature jusqu'a la date courante
            percent_empty = self.percent_time_empty_until(id_station, current_date)
            percent_saturated = self.percent_saturation_until(id_station, current_date)

            # Durees moyennes des episodes vides et satures jusqu'a la date courante
            mean_time_empty = self.average_empty_duration_until(id_station, current_date)
            mean_time_saturated = self.average_saturated_duration_until(id_station, current_date)

            if mean_time_empty is None:
                score_empty_duration = 0.5
            else:
                score_empty_duration = 1 - mean_time_empty / total_duration_hours

            if mean_time_saturated is None:
                score_saturated_duration = 0.5
            else:
                score_saturated_duration = 1 - mean_time_saturated / total_duration_hours

            score = (
                current_score
                + (1 - percent_empty)
                + (1 - percent_saturated)
                + score_empty_duration
                + score_saturated_duration
            ) / 5

            scores[current_date] = score

        return scores
