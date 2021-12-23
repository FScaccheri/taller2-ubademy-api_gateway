tags_metadata = [
    {
        "name": "login",
        "description": """Endpoint used to login the user, it receives a
        body with the following schema
        {
            email: str,
            password: str,
            expo_token: str
        }

        If the login was successful, it returns a Json Web Token used for
        operations validation, and if there is a problem it returns a message
        indicating what it was.
        """
    },
    {
        "name": "sign_up",
        "description": """Endpoint used to sign up the user, it receives a
        body with the following schema:
        {
            email: str,
            password: str,
            expo_token: str
        }

        If the sign up was successful, it returns a Json Web Token used for
        operations validation, and if there is a problem it returns a message
        indicating what it was.
        """
    },
    {
        "name": "oauth_login",
        "description": """Endpoint used to login the user, it receives a body
        with the following schema:
        {
            email: str,
            password: str,
            expo_token: str
        }

        If the login was successful, it returns a Json Web Token used for
        operations validation, and if there is a problem it returns a message
        indicating what it was.
        """
    },
    {
        "name": "admin_login",
        "description": """Checks if the user is registered as an admin. If he is
        and the password is correct" + "then it returns ok in status,
        otherwise it returns an error status and a message indicating the
        error. It receives a body with the following schema:
        {
            email: str
            password: str
            expo_token: str
        }
        """
    },
    {
        "name": "admin_register",
        "description": """Endpoint used to register an admin. It receives a
        body with the following schema:
        {
            email: str
            password: str
            expo_token: str
        }
        If the login was successful, it returns a Json Web Token used for
        operations validation, and if there is a problem it returns a message
        indicating what it was.
        """
    },
    {
        "name": "get_all_users",
        "description": """Endpoint used to get a list of all the users and
        if they are blocked or not. If there is a problem it returns a message
        indicating what it was.
        """
    },
    {
        "name": "courses/data/course_id",
        "description": """Endpoint to get the course's data. The level of data
        returned depends on the user's relationship with the course. If there
        was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/create_course",
        "description": """Endpoint used to create a course. It receives a
        body with the following schema:
        {
            title: str,
            description: str,
            total_exams: number,
            subscription_type: str,
            course_type: str,
            country: str,
            hashtags: array,
            images: array,
            videos: array
        }
        If the creation was successful, it returns the course's id. If there
        was a problem it returns a message indicating what it was
        """
    },
    {
        "name": "courses/update_course",
        "description": """Endpoint used to update a course. It receives a body
        with the following schema:
        {
            title: str,
            description: str,
            total_exams: number,
            subscription_type: str,
            course_type: str,
            country: str,
            hashtags: array,
            images: array,
            videos: array
        }
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/subscribe",
        "description": """Endpoint used to subscribe a user to a course. It
        receives a body with the following schema:
        {
            course_id: str
        }
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/unsubscribe",
        "description": """Endpoint used to subscribe a user to a course. It
        receives a body with the following schema:
        {
            course_id: str
        }
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/course_id/students",
        "description": """Endpoint used to get a list of the students from a
        course.
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "'courses/course_id/exam_name/students'",
        "description": """Endpoint used to get an exam. If students is none you
        will get the exam's questions. If students is a existing student, you
        will get the exam's questions, the student's answers and, in case the
        exam has been graded, you will get also the professor's grade.
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/course_id/exams/filter",
        "description": """Endpoint used to get a list of exams from a course.
        It recives a parameter that allows to filter the exams by
        published or not published.
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/course_id/students_exams/exam_filter",
        "description": """Endpoint used to get a list of exams from a course.
        It recives a parameter that a allows to filter the exams by
        graded, not graded and all.
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/course_id/exam/exam_name/exam_filter/student_email",
        "description": """Endpoint used to get a exam. It can recive the word
        questions or completed_exam. If it recive questions you will the
        exam's questions. If it recive completed_exams and a student you
        will get exam's grade (in case it was graded).
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "search_courses/course_type/subscription_type",
        "description": """Endpoint used to get a list of course filtered
        by course type and subscription type.
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/create_exam",
        "description": """Endpoint used to create an exam. It receives a body
        with the following schema:
        {
            course_id: str,
            questions: array,
            exam_name: str,
            exam_creator_email: str
        }
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/edit_exam",
        "description": """Endpoint used to edit a exam. To be able to edit an
        exam it must not have been published. It recives a body with the
        following schema:
        {
            course_id: str,
            questions: array,
            exam_name: str,
            exam_creator_email: str 
        }
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/publish_exam",
        "description": """Endpoint used to publish an exam. If there was a
        problem it returns a message indicating what it was."""
    },
    {
        "name": "courses/grade_exam",
        "description": """Endpoint used to grade an exam. It recives a body
        with the following schema:
        {
            course_id: str,
            corrections: array,
            exam_name: str,
            student_email: str,
            professor_email: str,
            mark: number
        }
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/complete_exam",
        "description": """Endpoint used to compleate an exam by a student. It
        recives a body with the following schema:
        {
            course_id: str,
            answers: array,
            exam_name: str,
            student_email: str
        }
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/add_collaborator",
        "description": """Endpoint that allows the course's creator to add
        an collaborator to the course. It recives a body with the following
        schema:
        {
            course_id: str,
            collaborator_email: str,
        }
        """
    },
        {
        "name": "profile_setup",
        "description": """Endpoint used to get all the requiered information to
        create a profile. If there was a problem it returns a message
        indicating what it was.
        """
    },
    {
        "name": "course_setup",
        "description": """Endpoint used to get all the requiered information to
        create a course. If there was a problem it returns a message indicating
        what it was.
        """
    },
    {
        "name": "update_profile",
        "description": """Endpoint used to update a user's profile. It
        recives a body with the following schema:
        {
            name: str,
            country: str,
            interesting_genres: array,
            subscription_type: str,
            profile_picture: str
        }
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "profile/profile_email",
        "description": """Endpoint used to get a user's public information to
        show it to another user. If there was a problem it returns a message
        indicating what it was.
        """
    },
    {
        "name": "modify_subscription",
        "description": """Endpoint used to know how much the user have to pay
        to change their subscription. It recives a body with the following
        schema:
        {
            new_subscription: str
        }
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "pay_subscription",
        "description": """Endpoint used to pay the user's new subscription. It
        recives a body with the following schema:
        {
            new_subscription: str
        }
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "my_courses",
        "description": """Endpoint used to get the user's courses. If there
        was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "course_genres",
        "description": """Endpoint used to get all the course types. If there
        was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "subscription_types",
        "description": """Endpoint used to get all the subscription types.
        If there was a problem it returns a message indicating what it was.
        """
    },
    {
        "name": "courses/passing",
        "description": """Endpoint used to get all the courses passed by an
        user. If there was a problem it returns a message indicating what it
        was.
        """
    },
    {
        "name": "change_blocked_status",
        "description": """Changes the account status of the received user based
        in the value received in is_blocked, if it is True then the user is
        blocked" + ", otherwise he is unblocked. Returns an ok status if the
        process was executed sucessfuly, otherwise it returns an error status
        with a message"""
    },
    {
        "name": "grade_course",
        "description": """Endpoint used to rate a course. It recives
        an review and a rating to rate the course. It
        recives a body with the following schema:
        {
            course_id: str,
            comment: str,
            grade: number
        }
        If there was a problem it
        returns a message indicating what it was.
        """
    },
    {
        "name": "student_gradings/id'",
        "description": """Endpoint used to get a course's rating. You will recive
        the rating and a list of reviews.
        """
    },
    {
        "name": "/users_metrics",
        "description": """Endpoint to fetch user related metrics.
        User metrics are: users amount, blocked users, non-blocked users, 
        last registered users, last logged users, last registered google users and 
        last logger google users.
        """
    },
    {
        "name": "/send_message",
        "description": """Endpoint to send a private message to another user in
        the app.
        """
    },
{
        "name": "/logout",
        "description": """Endpoint used to log a user out from the app.
        """
    }
]
