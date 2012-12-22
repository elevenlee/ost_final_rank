ost_final_rank
==============

The goal of the final project is to demonstrate your knowledge of Open
Source tools. In assignment 3, we wrote a command line tool to rank items,
and in assignment 4, we put together a simple web-based interface to this
system. For the final project, we will adapt this into a more full featured
web-based application.


I have wrote python doc in each '.py' file. Every class, function, and
method includes documentations.


The rank project has four main parts: Vote, Category, Item, and Other.

- Vote
  * Anyone can vote on any category
  * No need to login when voting as well as seeing result of category
  * When user want to vote, he/she must select a category first, the select
    category html page would list all categories of all users that have
    at least two items. After selecting a category, there would be two
    random items appear on the web page. User could select one of them to
    vote or skip this two random items. After the user voting, the voted
    result would appear on the top of web page and statistics of just voted
    items would also shown on the web page.
  * When user want to see result, click the result link page on the vote
    item page, all item in that specified category would be list ordered by
    win percentage in descending. If item has never been voted, a '--'
    character would appear in the percentage column.

- Category
  * Each category has a key in format 'author/category name'
  * Anyone can add category, only the creator of the category could edit and
    delete that specified category
  * Must login when add, edit, and delete category
  * When user add a category, the category name could not be empty, contains
    '/' character or already exist. If so, an error message would shown on
    the web page. After adding category successfully, the web page would
    redirect to the add item web page that you could add item for that
    specified category.
  * When user edit a category, the category name could not be empty,
    contains '/' character or already exist. If so, an error message would
    shown on the web page. After editing category name successfully, all
    items as well as comments belonging to that specified category would
    update their category information automatically. In the edit category
    name web page, user could also add, edit, delete items.
  * User could select any number of categories to delete, or click
    'Clear All' button to delete all categories. After deletion, all items
    as well as its comments belonging to specified categories would be
    deleted automatically.

- Item
  * Each item has a key in format 'author/category name/itemn name', and
    must have an ancestor category
  * Only the createor of the category could add, edit, delete item in that
    specified category
  * Must login when add, edit, and delete category
  * Before adding, editing, and deleting items, user must select a category.
  * When user add an item, all items that already in category would be
    shown at the top of web page. The item name could not be empty, contains
    '/' character or already exist. If so, an error message would shown on
    the web page. After adding item successfully, the web page would update.
  * When user edit an item, the item name could not be empty, contains '/'
    character or already exist. If so, an error message would shown on the
    web page. After editing item name successfully, all comments belonging
    to specified item would be deleted automatically.
  * User could select any number of items to delete, or click 'Clear All'
    button to delete all items. After deletion, all comments belonging to
    specified item would be deleted automatically.

- Other
  The other part itself has four minor parts: comment, search, import, and
  export.

  - Comment
    * Each comment has a key in format 'author/category name/item name/
      commenter', and must have an ancestor item
    * Anyone can submit comment  on any category, however user could submit
      comment on the specified item only once.
    * Must login when submit comment
    * When user want to submit a comment, he/she must select a category
      first, and then must select a item. After the selection, all comments
      for that specified item would appear at the bottom of web page. When
      user submiting a comment successfully, the comment web page would
      update.

  - Search
    * Anyone can search
    * No need to login when searching
    * When user want to search, he/she could input the keyword. After
      submition, the search result web page would have two parts: category
      result, and item result. In the category result, user could select a
      category to vote. In the item result, user could select an item to
      submit a comment. Notice: Voting do not need to login, while submiting
      comment need.

  - Import
    * Anyone can import XML file
    * Must login when importing XML file
    * Could only import one category at a time
    * Could only replace the user itself's category
    * When user want to import XML file, he/she must select a file. If not,
      an error message would be shown on the web page. After selecting a
      XML file, the system would check whether the category has already
      exist. If not, Adding the category and all items in the XML in the
      datastore. Otherwise, the system would delete all items that does not
      appear in the XML file, and then add all items in XML file that does
      not exist. Deletion would delete all belonging comments and vote
      vote result. Other items would be unchanged.

  - Export
    * Anyone can export XML file
    * No need to login when exporting XML file
    * Could only export one category at a time
    * Could export any users' category
    * When user want to export XML file, he/she must select a category
      first. If not, an error messgae would be shown on the web page. After
      selecting a category successfully, the system would export that
      specified category and all items belonging to a XML web page.
