from dfa_lib_python.ProvenanceObject import ProvenanceObject
from dfa_lib_python.set import Set
from dfa_lib_python.set_type import SetType


class Transformation(ProvenanceObject):
    """
    This class defines a dataflow transformation.

    Attributes:
        - tag (:obj:`str`): Transformation tag.
        - sets (:obj:`list`, optional): Transformation sets.
    """

    def __init__(self, tag, sets=[]):
        ProvenanceObject.__init__(self, tag.lower())
        self.sets = sets

    @property
    def sets(self):
        """Get or set the Transformation Sets."""
        return self._sets

    @sets.setter
    def sets(self, sets):
        assert isinstance(sets, list), "The Sets must be in a list."
        result = []
        for set in sets:
            assert isinstance(set, Set), "The Set must be valid."
            result.append(set.get_specification())
        self._sets = result

    @property
    def input(self):
        """Get or set the input Sets."""
        result = [x for x in self.sets if x["type"] == SetType.INPUT.value]
        return result

    @input.setter
    def input(self, sets):
        assert isinstance(sets, list), "The input Sets must be in a list."
        input_sets = []
        for set in sets:
            assert isinstance(set, Set), "The Set must be valid."
            assert set.type == SetType.INPUT.value, "The Set type must be INPUT."
            input_sets.append(set.get_specification())
        self._sets = [x for x in self.output] + input_sets

    @property
    def output(self):
        """Get or set the output Sets."""
        result = [x for x in self.sets if x["type"] == SetType.OUTPUT.value]
        return result

    @output.setter
    def output(self, sets):
        assert isinstance(sets, list), "The input Sets must be in a list."
        output_sets = []
        for set in sets:
            assert isinstance(set, Set), "The Set must be valid."
            assert set.type == SetType.OUTPUT.value, "The Set type must be OUTPUT."
            output_sets.append(set.get_specification())
        self._sets = [x for x in self.input] + output_sets

    def set_sets(self, sets):
        """ Set the transformation Sets collection.

        Args:
            - sets (:obj:`list`): An list containing :obj:`Set` objects.
        """
        assert isinstance(sets, list), "The parameter must be a list."
        for set in sets:
            self.add_set(set)

    def add_set(self, set):
        """ Add a Set to the transformation Sets collection.

        Args:
            - set (:obj:`Set`): A :obj:`Set` object..
        """
        assert isinstance(set, Set), "The set must be valid."
        self._sets.append(set.get_specification())


# Add transformation function
def tf(df, label, input_attr, output_attr, prev_out=None):
    """
    :param df: Dataflow tag
    :param label: Label for transformation
    :param input_attr: list of Attribute(label, type)
    :param output_attr: list of Attribute(label, type)
    :param prev_out: tf_output object of previous step:
    :return: tf, tf_input, tf_output
    """
    tf = Transformation(label)
    tf_input = Set(f"i{label}", SetType.INPUT, input_attr)
    tf_output = Set(f"o{label}", SetType.OUTPUT, output_attr)

    if prev_out:
        tf.set_sets([prev_out, tf_input, tf_output])
    else:
        tf.set_sets([tf_input, tf_output])
    df.add_transformation(tf)

    return tf, tf_input, tf_output
