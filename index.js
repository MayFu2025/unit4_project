const menubar = document.createElement('template')

menubar.innerHTML = `
    <div class="menubar">
        <button>Home</button>
        <h2>Following Clubs</h2>
        {% for cat in following %}
            <a href="{{url_for('get_category', cat_id=cat)}}">{{ cat }}</a>
        {% endfor %}
    </div>
`