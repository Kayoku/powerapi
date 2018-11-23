# Copyright (C) 2018  University of Lille
# Copyright (C) 2018  INRIA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Module actor_puller
"""

from smartwatts.actor import Actor, Handler


class _TimeoutHandler(Handler):
    """
    TimeoutHandler class
    """

    def __init__(self, database, filt):
        self.database = database
        self.filter = filt
        self.database.load()

    def handle(self, msg):
        """
        Override

        This handler read one report of the database and filter it,
        then return the tuple (report, dispatcher).
        """
        # Read one input, if it's None, it means there is not more
        # report in the database, just pass
        json = self.database.get_next()
        if json is None:
            return None

        # Deserialization
        report = self.filter.get_type()()
        report.deserialize(json)

        # Filter the report
        dispatcher = self.filter.route(report)
        return (report, dispatcher)


class ActorPuller(Actor):
    """ ActorPuller class """

    def __init__(self, name, database, filt, timeout, verbose=False):
        """
        Initialization

        Parameters:
            @database: BaseDB object
            @filter: Filter object
        """
        Actor.__init__(self, name, verbose, timeout=timeout)
        self.database = database
        self.filter = filt

    def setup(self):
        """
        Override

        Connect to all dispatcher in filter and define timeout_handler
        """

        # Connect to all dispatcher
        for _, dispatcher in self.filter.filters:
            dispatcher.connect(self.context)

        # Create handler
        self.timeout_handler = _TimeoutHandler(self.database, self.filter)

    def post_handle(self, msg):
        """
        Override

        Handle the send of the report to the good dispatcher
        """
        # Test if msg is None
        if msg is None:
            return

        # Extract report & dispatcher
        report = msg[0]
        dispatcher = msg[1]

        # Send to the dispatcher if it's not None
        if dispatcher is not None:
            dispatcher.send(report)
