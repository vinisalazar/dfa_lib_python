import requests
import os
from dfa_lib_python.ProvenanceObject import ProvenanceObject
from dfa_lib_python.dependency import Dependency
from dfa_lib_python.task_status import TaskStatus
from dfa_lib_python.dataset import DataSet
from dfa_lib_python.performance import Performance
from dfa_lib_python.element import Element
from datetime import datetime

dfa_url = os.environ.get("DFA_URL", "http://localhost:22000/")


class Task(ProvenanceObject):
    """
    This class defines a dataflow task.

    Attributes:
        - id (:obj:`str`): Task Id.
        - dataflow_tag (:obj:`str`): Dataflow tag.
        - transformation_tag (:obj:`str`): Transformation tag.
        - sub_id (:obj:`str`, optional): Task Sub Id.
        - dependency (:obj:`Task`): Task which the object has a dependency.
        - workspace (:obj:`str`, optional): Task workspace.
        - resource (:obj:`str`, optional): Task resource.
        - output (:obj:`str`, optional): Task output.
        - error (:obj:`str`, optional): Task error.
    """

    def __init__(
        self,
        id,
        dataflow_tag,
        transformation_tag,
        sub_id="",
        dependency=None,
        workspace="",
        resource="",
        output="",
        error="",
    ):
        ProvenanceObject.__init__(self, transformation_tag)
        self._workspace = workspace
        self._resource = resource
        self._dependency = ""
        self._output = output
        self._error = error
        self._sets = []
        self._status = TaskStatus.READY.value
        self._dataflow = dataflow_tag.lower()
        self._transformation = transformation_tag.lower()
        self._id = str(id)
        self._sub_id = sub_id
        self._performances = []
        self.dfa_url = dfa_url
        self.start_time = None
        self.end_time = None
        if isinstance(dependency, Task):
            dependency = Dependency([dependency._tag], [dependency._id])
            self._dependency = dependency.get_specification()

    def add_dependency(self, dependency):
        """ Add a dependency to the Task.

        Args:
            - dependency (:obj:`Dependency`): A :obj:`Dependency` object.
        """

        assert isinstance(dependency, Dependency), "The dependency must be valid."
        self._dependency = dependency.get_specification()

    def set_datasets(self, datasets):
        """ Set the Task DataSets.

        Args:
            - dataset (:obj:`list`): A :obj:`list` containing :obj:`DataSet` objects.
        """
        assert isinstance(datasets, list), "The parameter must be a list."
        for dataset in datasets:
            self.add_dataset(dataset)

    def add_dataset(self, dataset):
        """ Add a dataset to the Task.

        Args:
            - dataset (:obj:`DataSet`): A :obj:`DataSet` object.
        """
        assert isinstance(dataset, DataSet), "The dataset must be valid."
        self._sets.append(dataset.get_specification())

    def set_status(self, status):
        """ Change the Task Status.

        Args:
            - status (:obj:`TaskStatus`): A :obj:`TaskStatus` object.
        """
        assert isinstance(status, TaskStatus), "The task status must be valid."
        self._status = status.value

    def begin(self):
        """ Send a post request to the Dataflow Analyzer API to store the Task.
        """
        self.set_status(TaskStatus.RUNNING)
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save()

    def end(self):
        """ Send a post request to the Dataflow Analyzer API to store the Task.
        """
        self.set_status(TaskStatus.FINISHED)
        self.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        performance = Performance(self.start_time, self.end_time)
        self._performances.append(performance.get_specification())
        self.save()

    def save(self):
        """ Send a post request to the Dataflow Analyzer API to store the Task.
        """
        url = dfa_url + "/pde/task/json"
        message = self.get_specification()
        r = requests.post(url, json=message)
        print(r.status_code)


# Start task function
def start_task(task_id, dataflow_tag, label, in_elements):
    """
    :param task_id: Integer for each task (0, 1 ... n). Usually use with enumerate
    :param label: Same as corresponding Transformation labels
    :param elements: List of inputs
    :return: t, t_input, t_output
    """
    in_elements = [Element([i]) for i in in_elements]
    t = Task(task_id, dataflow_tag, label)
    t_input = DataSet(f"i{label}", in_elements)
    t.add_dataset(t_input)
    t.begin()

    return t, t_input


# End task function
def end_task(task, label, out_elements):
    """
    :param label: Same as Transformation
    :param out_elements: List of outputs
    :return:
    """
    t_output = DataSet(f"o{label}", [Element([i]) for i in out_elements])
    task.add_dataset(t_output)
    task.end()

    return t_output
