export function keepSelectVisible(list, currentIndex) {
    var itemHeight = list.getSize(0);
    var currentOffsetY = itemHeight * currentIndex;
    var viewHeight = list.getClientSize();
    var offset = list.getOffset();

    if (currentOffsetY + itemHeight > offset + viewHeight) {
        list.scrollToOffset(currentOffsetY - viewHeight + itemHeight);
    } else if (currentOffsetY < offset) {
        list.scrollToOffset(currentOffsetY);
    }
}

export function getListPageElementNumber(list) {
    var itemHeight = list.getSize(0);
    var viewHeight = list.getClientSize();

    return Math.floor(viewHeight / itemHeight);
}

export function updateListItemBackground(list, oldIndex, newIndex, backgroundColor, selectColor) {
    if (oldIndex !== null && oldIndex >= 0) {
        list[oldIndex].backgroundColor = backgroundColor;
    }

    if (newIndex !== null && newIndex >= 0) {
        list[newIndex].backgroundColor = selectColor;
    }
}

export function updateListItemMatchColor(list, oldIndex, newIndex, matchColor) {
    if (oldIndex !== null && oldIndex >= 0) {
        list[oldIndex].foregroundColor = "";
    }

    if (newIndex !== null && newIndex >= 0) {
        list[newIndex].foregroundColor = matchColor;
    }
}

export function updateListIndex(list, index) {
    if (index >= list.length) {
        return list.length - 1;
    } else if (index <= 0) {
        return 0;
    } else {
        return index;
    }
}

export function regsiterJsFunctions(object, eventNames) {
    const that = object;

    eventNames.forEach(eventName => {
        const camelCasedEventName = toCamelCase(eventName);
        if (typeof object[camelCasedEventName] === 'function') {
            object.$root.$on(eventName, () => {
                that[camelCasedEventName]();
            });
        } else {
            console.log(`Function '${camelCasedEventName}' not found`);
        }
    });
}

function toCamelCase(str) {
    const words = str.split('_');
    const camelCasedWords = words.map((word, index) => {
        if (index === 0) {
            return word;
        }
        return word[0].toUpperCase() + word.slice(1);
    });
    return camelCasedWords.join('');
}

/**
 * Layout, same as the Elisp custom variable "eaf-git-layout"
 */
export const Layout = {
    Horizontal: "H",
    Vertical: "V"
};
