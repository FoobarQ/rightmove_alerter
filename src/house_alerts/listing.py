class Listing:
    def __init__(
        self,
        user_id: str | None,
        listing_title: str,
        country: str,
        street_address: str,
        price: int,
        description: str,
        listing_url: str,
        image_url: str,
        notified: bool,
        id: str,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.listing_title = listing_title
        self.price = price
        self.description = description
        self.listing_url = listing_url
        self.country = country
        self.street_address = street_address
        self.image_url = image_url
        self.notified = notified

    def update_statement(self):
        query = "UPDATE house SET notified = true WHERE id = %s AND user_id = %s"
        args_tuple = (
            self.user_id,
            self.id,
        )
        return query, args_tuple

    def to_tuple(self, user_id: str, notified=False):
        return (
            self.id,
            self.listing_title,
            self.country,
            self.street_address,
            self.price,
            self.description,
            self.listing_url,
            self.image_url,
            notified,
            user_id,
        )

    def create_email_row(self):
        return f"""
            <tr>
                <td class="image">
                    <img src="{self.image_url}"/>
                </td>
                <td>
                    <div>
                        <h2>
                            <a href="{self.listing_url}">{self.listing_title}</a>
                        </h2>
                        <h5>{self.street_address} ({self.price})</h5>
                        <p style="word-break">{self.description}</p>
                    </div>
                </td>
            </tr>
            """

    def create_email_body(self):
        return f"""
        <html>
            <head>
                <style>
                    .image {{
                        width: 100px;
                        padding: 20px;
                    }}
                    @media screen and (min-width: 1200px) {{
                        .image {{
                            width: 600px;
                            padding: 20px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <table>
                    <tbody>
                        <tr>
                            <td class="image">
                                <img src="{self.image_url}"/>
                            </td>
                            <td>
                                <div>
                                    <h2>
                                        <a href="{self.listing_url}">{self.listing_title}</a>
                                    </h2>
                                    <h5>{self.street_address} ({self.price})</h5>
                                    <p style="word-break">{self.description}</p>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </body>
        </html>
        """

    def __str__(self):
        return f"""
        id:             {self.id}
        title:          {self.listing_title}
        street address: {self.street_address}
        country:        {self.country}
        price:          {self.price}
        description:    {self.description}
        url:            {self.listing_url}
        image_url:      {self.image_url}
        """
