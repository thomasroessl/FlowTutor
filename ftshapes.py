class FTShapes:

    @staticmethod
    def get_assignment_points():
        return [
            (0, 0),
            (150, 0),
            (150, 75),
            (0, 75),
            (0, 0)
        ]

    @staticmethod
    def get_conditional_points():
        return [
            (75, 0),
            (0, 50),
            (75, 100),
            (150, 50),
            (75, 0)
        ]

    @staticmethod
    def get_loop_points():
        return [
            (0, 37.5),
            (20, 75),
            (130, 75),
            (150, 37.5),
            (130, 0),
            (20, 0),
            (0, 37.5)
        ]

    @staticmethod
    def get_input_points():
        return [
            (20, 0),
            (150, 0),
            (130, 75),
            (0, 75),
            (20, 0)
        ]

    @staticmethod
    def get_output_points():
        return [
            (20, 0),
            (150, 0),
            (130, 75),
            (0, 75),
            (20, 0)
        ]