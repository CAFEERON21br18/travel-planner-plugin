"""The fixed travel-planner forms. Print them; never reword them.

  python3 questions.py form1 --lang en|pt|fr [--text]
  python3 questions.py form2 spec.json --lang .. [--text]     spec: which follow-ups apply (see SKILL.md)
  python3 questions.py choices choices.json --lang .. [--text]  the choices round after research

Default output is HTML for the form widget (Visualizer, module "elicitation"); --text prints the numbered fallback.
"""
import html, json, sys

HEAD_SVG = '<svg viewBox="0 0 20 20" fill="currentColor"><path d="M11.586 2a1.5 1.5 0 0 1 1.06.44l2.914 2.914a1.5 1.5 0 0 1 .44 1.06V16.5a1.5 1.5 0 0 1-1.5 1.5h-9a1.5 1.5 0 0 1-1.492-1.347L4 16.5v-13A1.5 1.5 0 0 1 5.5 2zM5.5 3a.5.5 0 0 0-.5.5v13a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V7h-2.5A1.5 1.5 0 0 1 11 5.5V3zm7.04 10.304a.5.5 0 0 1 .92.392c-.295.69-.871 1.304-1.66 1.304-.487 0-.892-.234-1.2-.574-.309.34-.713.574-1.2.574-.486 0-.892-.233-1.2-.574-.31.34-.714.574-1.2.574a.5.5 0 0 1 0-1c.212 0 .52-.18.74-.696l.034-.067a.5.5 0 0 1 .886.067c.221.516.528.696.74.696.213 0 .52-.18.74-.696l.035-.067a.5.5 0 0 1 .885.067c.22.516.527.696.74.696s.519-.18.74-.696m0-4a.5.5 0 0 1 .92.392c-.295.69-.871 1.304-1.66 1.304-.487 0-.892-.234-1.2-.574-.309.34-.713.574-1.2.574-.486 0-.892-.233-1.2-.574-.31.34-.714.574-1.2.574a.5.5 0 0 1 0-1c.212 0 .52-.18.74-.696l.034-.067a.5.5 0 0 1 .886.067c.221.516.528.696.74.696.213 0 .52-.18.74-.696l.035-.067a.5.5 0 0 1 .885.067c.22.516.527.696.74.696s.519-.18.74-.696M12 5.5a.5.5 0 0 0 .5.5h2.293L12 3.207z"/></svg>'
DROP_SVG = '<svg viewBox="0 0 20 20" fill="currentColor"><path d="M16.5 13a.5.5 0 0 1 .5.5v2a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 3 15.5v-2a.5.5 0 0 1 1 0v2a.5.5 0 0 0 .5.5h11a.5.5 0 0 0 .5-.5v-2a.5.5 0 0 1 .5-.5M10 3a.5.5 0 0 1 .374.168l4 4.5.059.082a.5.5 0 0 1-.732.65l-.075-.068L10.5 4.814V13.5a.5.5 0 0 1-1 0V4.814L6.374 8.332a.5.5 0 0 1-.748-.664l4-4.5.08-.071A.5.5 0 0 1 10 3"/></svg>'

# One entry per text; [en, pt, fr].
T = {
 "title": ["Trip details", "Detalhes da viagem", "Détails du voyage"],
 "title2": ["A few more details", "Mais alguns detalhes", "Encore quelques détails"],
 "title3": ["Pick your options", "Escolhe as opções", "Choisis tes options"],
 "skip": ["Skip", "Saltar", "Passer"], "go": ["Continue", "Continuar", "Continuer"],
 "other": ["Other", "Outro", "Autre"], "tell": ["Tell me more", "Diz-me mais", "Dis-m'en plus"],
 "blank": ["Leave anything blank if you don't know yet: I'll suggest options.", "Deixa em branco o que ainda não sabes: eu sugiro opções.", "Laisse vide ce que tu ne sais pas encore : je te proposerai des options."],
 "from": ["Where are you leaving from?", "De onde partes?", "D'où pars-tu ?"],
 "from_ph": ["City or airport", "Cidade ou aeroporto", "Ville ou aéroport"],
 "type": ["What kind of trip is it?", "Que tipo de viagem é?", "Quel type de voyage ?"],
 "road": ["Road trip", "Road trip", "Road trip"], "road_s": ["Driving from place to place", "De carro, de sítio em sítio", "En voiture, d'étape en étape"],
 "short": ["Short trip", "Viagem curta", "Court séjour"], "short_s": ["1 to 3 nights", "1 a 3 noites", "1 à 3 nuits"],
 "normal": ["Normal trip", "Viagem normal", "Voyage normal"], "normal_s": ["4 to 9 nights", "4 a 9 noites", "4 à 9 nuits"],
 "long": ["Long trip", "Viagem longa", "Long voyage"], "long_s": ["10 nights or more", "10 noites ou mais", "10 nuits ou plus"],
 "where": ["Where do you want to go?", "Para onde queres ir?", "Où veux-tu aller ?"],
 "where_ph": ["Country or region, or leave blank and I'll suggest 3 places", "País ou região, ou deixa em branco e eu sugiro 3 destinos", "Pays ou région, ou laisse vide et je te propose 3 destinations"],
 "ncities": ["How many cities do you want to see?", "Quantas cidades queres ver?", "Combien de villes veux-tu voir ?"],
 "cities_ph": ["Which ones, if you know (cities only)", "Quais, se já souberes (só cidades)", "Lesquelles, si tu sais (villes seulement)"],
 "who": ["Who is going?", "Quem vai?", "Qui part ?"],
 "who_ph": ["e.g. 2 adults, kids aged 6 and 9", "ex.: 2 adultos, crianças de 6 e 9 anos", "ex. : 2 adultes, enfants de 6 et 9 ans"],
 "sleep": ["Where do you want to sleep?", "Onde queres dormir?", "Où veux-tu dormir ?"],
 "hotel": ["Hotel", "Hotel", "Hôtel"], "house": ["House or flat", "Casa ou apartamento", "Maison ou appartement"], "van": ["Van (road trip)", "Carrinha (road trip)", "Van (road trip)"],
 "bnb": ["B&B", "B&B", "Chambre d'hôtes"], "resort": ["Resort", "Resort", "Resort"], "camp": ["Campsite", "Parque de campismo", "Camping"],
 "hostel": ["Hostel", "Hostel", "Auberge"], "have": ["I already have a place", "Já tenho onde ficar", "J'ai déjà un logement"],
 "there": ["How do you want to get there? (not needed for a road trip)", "Como queres lá chegar? (não é preciso num road trip)", "Comment veux-tu y aller ? (inutile pour un road trip)"],
 "plane": ["Plane", "Avião", "Avion"], "train": ["Train", "Comboio", "Train"], "bus": ["Bus", "Autocarro", "Bus"], "boat": ["Boat", "Barco", "Bateau"], "owncar": ["Own car", "Carro próprio", "Ma voiture"],
 "purpose": ["What is the trip mainly for? (pick several)", "Qual é o objetivo da viagem? (podes escolher vários)", "C'est surtout pour quoi ? (plusieurs choix)"],
 "sport": ["Sport", "Desporto", "Sport"], "sport_s": ["Surf, snow, hiking…", "Surf, neve, caminhadas…", "Surf, neige, randonnée…"],
 "culture": ["Cultural", "Cultural", "Culturel"], "culture_s": ["Museums, history", "Museus, história", "Musées, histoire"],
 "exp": ["Experience", "Experiência", "Expérience"], "exp_s": ["Something special to live", "Algo especial para viver", "Quelque chose de spécial à vivre"],
 "disc": ["Discovery", "Descoberta", "Découverte"], "disc_s": ["See as much as you can", "Ver o máximo possível", "Voir un maximum"],
 "friends": ["Friends trip", "Viagem com amigos", "Voyage entre amis"], "friends_s": ["Share the plan with them", "Partilha o plano com eles", "Partage le plan avec eux"],
 "relax": ["Relax", "Descansar", "Détente"], "relax_s": ["Beach, pool, slow days", "Praia, piscina, dias calmos", "Plage, piscine, jours calmes"],
 "food": ["Food and wine", "Comida e vinho", "Gastronomie et vin"], "food_s": ["Restaurants, markets, tastings", "Restaurantes, mercados, provas", "Restaurants, marchés, dégustations"],
 "nature": ["Nature", "Natureza", "Nature"], "nature_s": ["Parks, viewpoints, walks", "Parques, miradouros, passeios", "Parcs, points de vue, balades"],
 "family": ["Family", "Família", "Famille"], "family_s": ["Things kids enjoy", "Coisas de que as crianças gostam", "Pour les enfants aussi"],
 "budget": ["What is your budget?", "Qual é o teu orçamento?", "Quel est ton budget ?"],
 "budget_ph": ["Amount in €, e.g. 1200", "Valor em €, ex.: 1200", "Montant en €, ex. : 1200"],
 "total": ["Total", "Total", "Total"], "pp": ["Per person", "Por pessoa", "Par personne"], "strict": ["Strict", "Fixo", "Strict"], "flex": ["Flexible", "Flexível", "Flexible"],
 "around": ["How will you get around there?", "Como te vais deslocar lá?", "Comment te déplaceras-tu sur place ?"],
 "foot": ["On foot", "A pé", "À pied"], "rental": ["Rental car", "Carro alugado", "Voiture de location"], "public": ["Public transport", "Transportes públicos", "Transports en commun"],
 "taxi": ["Taxi or ride-hailing", "Táxi ou TVDE", "Taxi ou VTC"], "bike": ["Bike or scooter", "Bicicleta ou trotinete", "Vélo ou trottinette"], "tours": ["Tours and transfers", "Tours e transfers", "Excursions et transferts"],
 "dates": ["When are you going?", "Quando vais?", "Quand pars-tu ?"],
 "start": ["First day", "Primeiro dia", "Premier jour"], "end": ["Last day", "Último dia", "Dernier jour"],
 "dates_ph": ["Or: the month and how many days", "Ou: o mês e quantos dias", "Ou : le mois et combien de jours"],
 "flexdates": ["How flexible are the dates?", "Quão flexíveis são as datas?", "Les dates sont-elles flexibles ?"],
 "exact": ["Exact", "Exatas", "Exactes"], "pm2": ["± 2 days", "± 2 dias", "± 2 jours"], "pmw": ["± 1 week", "± 1 semana", "± 1 semaine"], "month": ["Any time that month", "Qualquer altura nesse mês", "N'importe quand ce mois-là"],
 "pace": ["What pace do you like?", "Que ritmo preferes?", "Quel rythme préfères-tu ?"],
 "relaxed": ["Relaxed", "Calmo", "Tranquille"], "balanced": ["Balanced", "Equilibrado", "Équilibré"], "packed": ["Packed", "Intenso", "Chargé"],
 "must": ["What do you most want to see and experience there?", "O que mais queres ver e viver lá?", "Qu'est-ce que tu veux surtout voir et vivre là-bas ?"],
 "must_ph": ["Must-sees, and anything to avoid", "O que não podes perder, e o que evitar", "Les incontournables, et ce qu'il faut éviter"],
 "extra": ["Anything else I should know?", "Mais alguma coisa que eu deva saber?", "Autre chose à savoir ?"],
 "extra_ph": ["Diet, mobility, pets, nationality (for entry rules), language of the documents, what is already booked…", "Alimentação, mobilidade, animais, nacionalidade (regras de entrada), língua dos documentos, o que já está reservado…", "Régime, mobilité, animaux, nationalité (règles d'entrée), langue des documents, ce qui est déjà réservé…"],
 "bookings": ["Already booked something? Add the confirmations", "Já reservaste alguma coisa? Junta as confirmações", "Déjà réservé quelque chose ? Ajoute les confirmations"],
 "choose": ["Choose file", "Escolher ficheiro", "Choisir un fichier"],
 # Form 2
 "pickdest": ["Which of these places do you like best?", "Qual destes destinos preferes?", "Laquelle de ces destinations préfères-tu ?"],
 "onway": ["Places you want to see on the way", "Sítios que queres ver pelo caminho", "Endroits à voir en chemin"],
 "onway_ph": ["Towns, viewpoints, beaches…", "Vilas, miradouros, praias…", "Villages, points de vue, plages…"],
 "stops": ["How many stops on the way?", "Quantas paragens pelo caminho?", "Combien d'arrêts en chemin ?"],
 "stops_rec": ["Recommended: {n} (a break about every 2 h of driving, plus scenic stops)", "Recomendado: {n} (uma pausa a cada 2 h de condução, mais paragens bonitas)", "Conseillé : {n} (une pause toutes les 2 h de route, plus les beaux arrêts)"],
 "car": ["Which car? (to estimate fuel, tolls and charging)", "Que carro? (para estimar combustível, portagens e carregamentos)", "Quelle voiture ? (pour estimer carburant, péages et recharges)"],
 "car_ph": ["Make and model, e.g. Renault Clio 1.0", "Marca e modelo, ex.: Renault Clio 1.0", "Marque et modèle, ex. : Renault Clio 1.0"],
 "fuel": ["Fuel", "Combustível", "Carburant"], "petrol": ["Petrol", "Gasolina", "Essence"], "diesel": ["Diesel", "Gasóleo", "Diesel"], "hybrid": ["Hybrid", "Híbrido", "Hybride"], "ev": ["Electric", "Elétrico", "Électrique"],
 "flights": ["How many flights each way are you OK with?", "Quantos voos por sentido aceitas?", "Combien de vols par trajet acceptes-tu ?"],
 "direct": ["1 (direct only)", "1 (só direto)", "1 (direct seulement)"], "f2": ["2 (one connection)", "2 (uma escala)", "2 (une escale)"], "f3": ["3 or more", "3 ou mais", "3 ou plus"],
 "nfriends": ["How many of you are going?", "Quantos vão?", "Combien êtes-vous ?"],
 "contacts": ["Emails or phone numbers to share the trip with (optional)", "Emails ou telefones com quem partilhar a viagem (opcional)", "E-mails ou numéros avec qui partager le voyage (facultatif)"],
 "contacts_ph": ["One per line. They are only used for the message I prepare for you.", "Um por linha. Só servem para a mensagem que preparo para ti.", "Un par ligne. Ils servent seulement au message que je te prépare."],
 "level": ["Your level", "O teu nível", "Ton niveau"], "beg": ["Beginner", "Iniciante", "Débutant"], "mid": ["Intermediate", "Intermédio", "Intermédiaire"], "adv": ["Advanced", "Avançado", "Avancé"],
 "gear": ["Gear", "Material", "Matériel"], "owngear": ["My own", "O meu", "Le mien"], "rent": ["Rent it there", "Alugar lá", "Louer sur place"],
 "lessons": ["Lessons?", "Aulas?", "Des cours ?"], "yes": ["Yes", "Sim", "Oui"], "no": ["No", "Não", "Non"],
 "flygear": ["Flying with a board or skis?", "Vais voar com prancha ou esquis?", "Tu prends l'avion avec une planche ou des skis ?"],
 "driver": ["Main driver's age and years with a licence (rental firms often have a minimum age and a young-driver fee)", "Idade do condutor principal e anos de carta (as rent-a-car têm idade mínima e taxa para jovens condutores)", "Âge du conducteur principal et années de permis (les loueurs ont souvent un âge minimum et des frais jeune conducteur)"],
 "driver_ph": ["e.g. 19, licence since 2025", "ex.: 19, carta desde 2025", "ex. : 19 ans, permis depuis 2025"],
}
LANGS = {"en": 0, "pt": 1, "fr": 2}


class F:
    def __init__(self, lang):
        self.i = LANGS.get(lang, 0); self.parts = []; self.text = []; self.n = 0

    def t(self, k, **kw):
        return T[k][self.i].format(**kw)

    def q(self, k, **kw):
        self.n += 1; s = self.t(k, **kw); self.text.append(f"\n{self.n}. {s}"); return html.escape(s)

    def group(self, inner, label):
        self.parts.append(f'<div class="elicit-group"><label class="elicit-question">{label}</label>{inner}</div>')

    def pills(self, name, keys, multi=False, other=False, label=None, accent=None):
        lab = label if label is not None else self.q(name)
        b = "".join(f'<button type="button" class="elicit-pill" data-value="{html.escape(self.t(k))}"{f" data-accent={chr(34)}{accent}{chr(34)}" if accent else ""}>{html.escape(self.t(k))}</button>' for k in keys)
        if other: b += f'<button type="button" class="elicit-pill" data-value="Other" data-other>{self.t("other")}</button>'
        self.text.append("   " + " / ".join(self.t(k) for k in keys) + (f" / {self.t('other')}" if other else "") + (" (several)" if multi else ""))
        o = f'<input type="text" class="elicit-other" data-for="{name}" placeholder="{self.t("tell")}" hidden>' if other else ""
        return f'<div class="elicit-pills" data-name="{name}" data-multi="{str(multi).lower()}">{b}</div>{o}', lab

    def cards(self, name, items, multi=False, label_key=None):
        lab = self.q(label_key or name)
        st = 'style="border-radius:12px; padding:14px 16px; display:flex; gap:12px; align-items:flex-start; text-align:left; min-width:180px; box-shadow:0 1px 2px rgba(0,0,0,0.04)"'
        b = "".join(f'<button type="button" class="elicit-pill" data-value="{html.escape(self.t(k))}" {st}><i class="ti ti-{icon}" style="font-size:20px" aria-hidden="true"></i><span><span style="font-size:13px; font-weight:500">{html.escape(self.t(k))}</span><br><span style="font-size:11px; color:var(--text-muted)">{html.escape(self.t(k + "_s"))}</span></span></button>' for k, icon in items)
        self.text.append("   " + " / ".join(f"{self.t(k)} ({self.t(k + '_s')})" for k, _ in items) + (" (several)" if multi else ""))
        self.group(f'<div class="elicit-pills" data-name="{name}" data-multi="{str(multi).lower()}">{b}</div>', lab)

    def textarea(self, name, ph, label_key=None):
        lab = self.q(label_key or name)
        self.text.append(f"   ({self.t(ph)})")
        self.group(f'<textarea class="elicit-textarea" data-name="{name}" rows="2" placeholder="{html.escape(self.t(ph))}"></textarea>', lab)

    def form(self, title_key):
        intro = f'<p style="font-size:13px;color:var(--text-muted);margin:0 0 4px">{html.escape(self.t("blank"))}</p>' if title_key == "title" else ""
        return (f'<form class="elicit"><div class="elicit-header">{HEAD_SVG}<span>{self.t(title_key)}</span></div><div class="elicit-body">{intro}{"".join(self.parts)}</div>'
                f'<div class="elicit-footer"><button type="button" class="elicit-skip">{self.t("skip")}</button><button type="button" class="elicit-submit">{self.t("go")}</button></div></form>')


def form1(lang):
    f = F(lang)
    f.textarea("from", "from_ph")
    f.cards("trip_type", label_key="type", items=[("road", "road"), ("short", "clock-hour-3"), ("normal", "calendar-week"), ("long", "world")])
    f.textarea("destination", "where_ph", "where")
    lab = f.q("ncities"); f.text.append(f"   1–8 · ({f.t('cities_ph')})")
    f.group('<input type="range" data-name="cities" min="1" max="8" step="1" value="2" style="width:100%"><div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-muted)"><span>1</span><span>8</span></div>'
            f'<textarea class="elicit-textarea" data-name="which_cities" rows="1" placeholder="{html.escape(f.t("cities_ph"))}"></textarea>', lab)
    f.textarea("travellers", "who_ph", "who")
    f.group(*f.pills("sleep", ["hotel", "house", "van", "bnb", "resort", "camp", "hostel", "have"], multi=True, other=True))
    f.group(*f.pills("getting_there", ["plane", "train", "bus", "boat", "owncar"], multi=True, other=True, label=f.q("there")))
    f.cards("purpose", [("sport", "ripple"), ("culture", "building-bank"), ("exp", "sparkles"), ("disc", "compass"), ("friends", "users"), ("relax", "beach"), ("food", "glass-full"), ("nature", "trees"), ("family", "mood-kid")], multi=True)
    lab = f.q("budget"); p1, _ = f.pills("budget_basis", ["total", "pp"], label=""); p2, _ = f.pills("budget_kind", ["strict", "flex"], label="")
    f.text.append(f"   ({f.t('budget_ph')})")
    f.group(f'<textarea class="elicit-textarea" data-name="budget" rows="1" placeholder="{html.escape(f.t("budget_ph"))}"></textarea>{p1}{p2}', lab)
    f.group(*f.pills("getting_around", ["foot", "owncar", "rental", "public", "taxi", "bike", "tours"], multi=True, other=True, label=f.q("around")))
    lab = f.q("dates"); f.text.append(f"   {f.t('start')} / {f.t('end')} ({f.t('dates_ph')})")
    f.group(f'<div style="display:flex;gap:12px;flex-wrap:wrap"><label style="font-size:12px">{f.t("start")}<br><input type="date" class="elicit-date" data-name="start"></label>'
            f'<label style="font-size:12px">{f.t("end")}<br><input type="date" class="elicit-date" data-name="end"></label></div>'
            f'<textarea class="elicit-textarea" data-name="dates_text" rows="1" placeholder="{html.escape(f.t("dates_ph"))}"></textarea>', lab)
    f.group(*f.pills("date_flex", ["exact", "pm2", "pmw", "month"], label=f.q("flexdates")))
    f.group(*f.pills("pace", ["relaxed", "balanced", "packed"]))
    f.textarea("must_see", "must_ph", "must")
    lab = f.q("extra"); f.text.append(f"   ({f.t('extra_ph')})")
    f.group(f'<textarea class="elicit-textarea" data-name="extra" rows="2" placeholder="{html.escape(f.t("extra_ph"))}"></textarea>', lab)
    lab = f.q("bookings")
    f.group(f'<div class="elicit-files" data-name="bookings"><label class="elicit-dropzone">{DROP_SVG}<span>{f.t("choose")}</span><input type="file" multiple></label></div>', lab)
    return f, f.form("title")


def form2(spec, lang):
    """spec keys (include only what applies): destinations:[{name,why,budget,months}], road:{recommended_stops},
    car:true, flights:true, friends:{count}, sport:true, rental:true"""
    f = F(lang)
    if spec.get("destinations"):
        lab = f.q("pickdest")
        st = 'style="border-radius:12px; padding:14px 16px; display:flex; flex-direction:column; gap:4px; text-align:left; min-width:200px; box-shadow:0 1px 2px rgba(0,0,0,0.04)"'
        b = "".join(f'<button type="button" class="elicit-pill" data-value="{html.escape(d["name"])}" {st}><span style="font-size:13px; font-weight:500">{html.escape(d["name"])}</span><span style="font-size:11px; color:var(--text-muted)">{html.escape(d.get("why", ""))}</span><span style="font-size:11px; color:var(--text-muted)">{html.escape(" · ".join(x for x in [d.get("budget", ""), d.get("months", "")] if x))}</span></button>' for d in spec["destinations"])
        f.text.append("   " + " / ".join(d["name"] for d in spec["destinations"]))
        f.group(f'<div class="elicit-pills" data-name="destination" data-multi="false">{b}<button type="button" class="elicit-pill" data-value="Other" data-other>{f.t("other")}</button></div><input type="text" class="elicit-other" data-for="destination" placeholder="{f.t("tell")}" hidden>', lab)
    if spec.get("road"):
        n = int(spec["road"].get("recommended_stops", 2))
        f.textarea("on_the_way", "onway_ph", "onway")
        lab = f.q("stops"); rec = html.escape(f.t("stops_rec", n=n)); f.text.append("   " + f.t("stops_rec", n=n))
        f.group(f'<input type="range" data-name="stops" min="0" max="{max(8, n * 2)}" step="1" value="{n}" style="width:100%"><div style="font-size:11px;color:var(--text-muted)">{rec}</div>', lab)
    if spec.get("car"):
        lab = f.q("car"); p, _ = f.pills("fuel", ["petrol", "diesel", "hybrid", "ev"], label="")
        f.text.append(f"   ({f.t('car_ph')})")
        f.group(f'<textarea class="elicit-textarea" data-name="car" rows="1" placeholder="{html.escape(f.t("car_ph"))}"></textarea>{p}', lab)
    if spec.get("flights"):
        f.group(*f.pills("max_flights", ["direct", "f2", "f3"], label=f.q("flights")))
    if spec.get("friends"):
        c = int(spec["friends"].get("count", 4))
        lab = f.q("nfriends"); f.text.append("   2–12")
        f.group(f'<input type="range" data-name="friends" min="2" max="12" step="1" value="{c}" style="width:100%">', lab)
        f.textarea("contacts", "contacts_ph", "contacts")
    if spec.get("sport"):
        f.group(*f.pills("level", ["beg", "mid", "adv"], label=f.q("level")))
        f.group(*f.pills("gear", ["owngear", "rent"], label=f.q("gear")))
        f.group(*f.pills("lessons", ["yes", "no"], label=f.q("lessons")))
        f.group(*f.pills("fly_with_gear", ["yes", "no"], label=f.q("flygear")))
    if spec.get("rental"):
        f.textarea("driver", "driver_ph", "driver")
    return f, (f.form("title2") if f.parts else "")


def choices(spec, lang):
    """spec: [{id, question, options:[{title, lines:[...], price?}], recommended?: index}]"""
    f = F(lang)
    st = 'style="border-radius:12px; padding:14px 16px; display:flex; flex-direction:column; gap:3px; text-align:left; min-width:200px; max-width:280px; box-shadow:0 1px 2px rgba(0,0,0,0.04)"'
    for c in spec:
        f.n += 1; f.text.append(f"\n{f.n}. {c['question']}")
        b = ""
        for k, o in enumerate(c["options"]):
            rec = " ★" if c.get("recommended") == k else ""
            b += (f'<button type="button" class="elicit-pill" data-value="{html.escape(o["title"])}" {st}><span style="font-size:13px; font-weight:500">{html.escape(o["title"])}{rec}</span>'
                  + "".join(f'<span style="font-size:11px; color:var(--text-muted)">{html.escape(l)}</span>' for l in o.get("lines", []))
                  + (f'<span style="font-size:12px; font-weight:500">{html.escape(o["price"])}</span>' if o.get("price") else "") + "</button>")
            f.text.append(f"   {chr(97 + k)}) {o['title']}{rec}: " + " · ".join(o.get("lines", []) + ([o["price"]] if o.get("price") else [])))
        f.group(f'<div class="elicit-pills" data-name="{html.escape(c["id"])}" data-multi="false">{b}</div>', html.escape(c["question"]))
    return f, f.form("title3")


if __name__ == "__main__":
    a = sys.argv[1:]
    lang = a[a.index("--lang") + 1] if "--lang" in a else "en"
    if a[0] == "form1":
        f, h = form1(lang)
    elif a[0] == "form2":
        f, h = form2(json.load(open(a[1])), lang)
    else:
        f, h = choices(json.load(open(a[1])), lang)
    print("\n".join(f.text).strip() if "--text" in a else h)
